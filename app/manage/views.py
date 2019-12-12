# coding=utf-8
# python3

from flask import render_template, redirect, url_for, make_response, request, current_app, flash, send_from_directory, Response
from app.manage import manage
from app import db
from flask_login import current_user, login_required
import pandas as pd
import os
from io import BytesIO
from openpyxl.styles import Font
from app.common.logger import create_logger

logger = create_logger(__name__)


@manage.route("/")
@login_required
def index():
    return render_template("manage/index.html")


@manage.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("excel")
        filename = file.filename
        allowed_extensions = ["xls", "xlsx"]
        if "." in filename and filename.split(".")[-1] in allowed_extensions:
            df = pd.read_excel(file)
            df.to_sql("t_excel", con=db.engine, index=False, if_exists="append", chunksize=1000)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], "{}-{}".format(current_user.username, filename)))
            status = "success"
            flash(status.capitalize() + ": upload completed.")
        else:
            status = "danger"
            flash(status.capitalize() + ": file type must be xls or xlsx.")
        return render_template("manage/upload.html", status=status)
    return render_template("manage/upload.html")


@manage.route("/download", methods=["GET", "POST"])
@login_required
def download():
    sql = "select concat(table_schema,'.',table_name) as table_name from information_schema.tables where table_schema='flasky'"
    tables = pd.read_sql(sql=sql, con=db.engine)["table_name"].tolist()
    return render_template("manage/download.html", tables=tables)


@manage.route("/query", methods=["GET", "POST"])
@login_required
def query():
    data = {
        "databases": [],
        "tables": [],
        "columns": [],
        "data": []
    }
    filter_schema = ["performance_schema", "sys", "mysql", "_toadls", "cr_debug", "questdebug", "questsoftware"]
    sql_databases = "select schema_name from information_schema.schemata where schema_name not in ('{}')".format("','".join(filter_schema))
    df_database = pd.read_sql(sql=sql_databases, con=db.engine)
    data["databases"] = df_database["schema_name"].tolist()

    sql_tables = "select table_schema,table_name from information_schema.tables where table_schema not in ('{}')".format("','".join(filter_schema))
    df_table = pd.read_sql(sql=sql_tables, con=db.engine)
    data["tables"] = df_table.to_dict("records")

    if request.method == "POST":
        sql = request.form["sql"]
        logger.info(sql)
        try:
            df_row = pd.read_sql(sql=sql, con=db.engine)
            data["columns"] = df_row.to_dict("split")["columns"]
            data["data"] = df_row.to_dict("split")["data"]
        except Exception as e:
            print("e:", e.__dict__)
            print("args", e.args)
            if hasattr(e, "orig"):
                flash(e.orig)
            else:
                flash(e)

    return render_template("manage/query.html", data=data)


@manage.route("/download/<filename>", methods=['GET'])
@login_required
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    # directory = os.getcwd()  # 假设在当前目录
    # print(directory)
    # return send_from_directory(directory, filename, as_attachment=True)

    chunksize = 1000
    file = BytesIO()
    logger.info("step 1")
    # df = pd.read_sql("select * from posts limit 10000", con=db.engine, chunksize=chunksize)
    df = pd.read_sql("select * from {}".format(filename), con=db.engine, chunksize=chunksize)
    # xlwt不支持存储为xlsx，所以使用其他扩展
    # writer = pd.ExcelWriter(file, engine='xlwt')
    logger.info("step 2")
    writer = pd.ExcelWriter(file, engine='openpyxl')
    # df.to_excel(writer, index=False)
    i = 0
    for df_tmp in df:
        logger.info(i)
        df_tmp.to_excel(writer, index=False, startrow=i * chunksize)
        i += 1

    for row in writer.sheets["Sheet1"]:
        for cell in row:
            # Font(name='等线', size=24, italic=True, color=colors.RED, bold=True)
            cell.font = Font(size=8)
    writer.save()  # 这个save不会落盘，后面不要接writer.close()

    logger.info("setp 3")
    resp = make_response(file.getvalue())
    resp.mimetype = "application/octet-stream"

    logger.info("step 4")
    # resp.headers["Content-type"] = "application/vnd.ms-excel"               # 指定返回的类型xls
    # resp.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # 指定返回的类型xlsx
    resp.headers["Transfer-Encoding"] = "chunked"  # 代表这个报文采用了分块编码。这时，报文中的实体需要改为用一系列分块来传输
    resp.headers["Content-Disposition"] = "attachment;filename={}.xlsx".format(filename)  # 设定用户浏览器显示
    logger.info("step 5")
    return resp


@manage.route("/download_flow/<filename>", methods=['GET'])
@login_required
def download_flow(filename):
    chunksize = 10000000
    df = pd.read_sql("select * from {} limit 10".format(filename), con=db.engine, chunksize=chunksize)

    def generate():
        for df_tmp in df:
            # 类型判断，非数字字段内容需要使用双引号括起来
            print(df_tmp.dtypes)
            print(df_tmp)
            print(df_tmp.to_dict("split")["data"])
            res = ""
            for index, row in df_tmp.iterrows():
                print(row.to_records())
            yield ",".join(row) + "\n"

    # resp = Response(generate(), mimetype='application/gzip')
    resp = Response(generate(), mimetype='text/csv')
    # resp.headers["Transfer-Encoding"] = "chunked"  # 代表这个报文采用了分块编码。这时，报文中的实体需要改为用一系列分块来传输
    resp.headers["Content-Disposition"] = "attachment;filename={}.csv".format(filename)  # 设定用户浏览器显示
    return resp
