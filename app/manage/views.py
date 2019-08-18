# coding=utf-8
# python3

from flask import render_template, redirect, url_for, make_response, request, current_app, flash, send_from_directory
from app.manage import manage
from app import db
from flask_login import current_user, login_required
import pandas as pd
import os


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
    tables = []
    sql = "select concat(table_schema,'.',table_name) as table_name from information_schema.tables"
    for row in db.engine.execute(sql):
        tables.append(row["table_name"])
    return render_template("manage/download.html", tables=tables)


@manage.route("/query", methods=["GET", "POST"])
@login_required
def query():
    data = {
        "select_database": "",
        "databases": [],
        "tables": [],
        "columns": [],
        "data": []
    }
    sql_databases = "select schema_name from information_schema.schemata"
    for row in db.engine.execute(sql_databases):
        data["databases"].append(row["schema_name"])

    data["select_database"] = data["databases"][0]
    if request.method == "POST":
        data["select_database"] = request.form["database"]
        sql = request.form["sql"]
        print(sql)
        try:
            rows = db.engine.execute(sql)
            data["columns"] = rows.keys()
            for row in rows:
                data["data"].append(row)
        except Exception as e:
            print("e:", e.__dict__)
            print("args", e.args)
            if hasattr(e, "orig"):
                flash(e.orig)
            else:
                flash(e)

    sql_tables = "select table_name from information_schema.tables where table_schema='{}'".format(data["select_database"])
    for row in db.engine.execute(sql_tables):
        data["tables"].append(row["table_name"])

    return render_template("manage/query.html", data=data)


@manage.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    print(directory)
    return send_from_directory(directory, filename, as_attachment=True)
