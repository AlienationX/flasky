# coding=utf-8
# python3

import pandas as pd
from flask import request, jsonify, abort, url_for, g
from math import ceil

from app.api import api
from app import db
from app.api.auth import auth
from app.common.logger import create_logger
from conf.config import Config

logger = create_logger(__name__)


@api.route("/posts", methods=["GET"])
@auth.login_required
def get_posts():
    # scope in ("all", "user")
    scope = request.args.get("scope") or "all"
    offset = request.args.get("offset") or Config.DEFAULT_OFFSET
    limit = request.args.get("limit") or Config.DEFAULT_LIMIT
    if scope == "all":
        where = ""
    else:
        where = "where p.author_id=".format()

    sql = """
    select p.id,p.body,p.create_time,p.author_id,u.username as author_name
    from posts p
    left join users u on p.author_id=u.id
    {where}
    order by create_time desc 
    limit {offset},{limit}
    """.format(where=where, offset=offset, limit=limit)
    logger.debug(sql)
    df = pd.read_sql(sql, con=db.engine)
    df["uri"] = df["id"].map(lambda x: url_for("api.get_post", id=x, _external=True))
    data = df.to_dict("records")
    print(data)

    sql1 = "select count(1) from posts p {where}".format(where=where)
    logger.debug(sql1)
    df1 = pd.read_sql(sql1, con=db.engine)
    total_count = df1.iat[0, 0]

    # TypeError: Object of type 'int64' is not JSON serializable
    # total_count需要类型转换
    summary = {
        "total_count": int(total_count),
        "total_page": ceil(total_count / int(limit))
    }
    return {"data": data, "summary": summary, "message": "OK"}


@api.route("/posts/<int:id>", methods=["GET"])
@auth.login_required
def get_post(id):
    sql = """
    select p.id,p.body,p.create_time,p.author_id,u.username as author_name from posts p left join users u on p.author_id=u.id where id={}
    """.format(id)
    logger.debug(sql)
    df = pd.read_sql(sql, con=db.engine)
    data = df.to_dict("records")
    return {"data": data, "message": "OK"}


@api.route("/posts", methods=["POST"])
@auth.login_required
def add_post():
    # Location 是添加的 header
    # data = request.json
    # data = request.get_json()
    data = request.get_json()
    body = data["body"]
    author_id = data["author_id"]
    sql = "insert into posts (body,author_id) values ('{}',{})".format(body, author_id)
    logger.debug(sql)
    db.session.execute(sql)
    db.session.commit()
    return {"data": request.json, "message": "created"}, 201, {"Location": url_for("api.get_post", id=99)}


@api.route("/posts/<int:id>", methods=["PUT"])
@auth.login_required
def update_post(id):
    data = request.get_json()
    body = data["body"]
    sql = "update posts set body='{}' where id={}".format(body, id)
    logger.debug(sql)
    db.session.execute(sql)
    db.session.commit()
    return {"data": sql, "message": "updated success id:{}".format(id)}, 200


@api.route("/posts/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_post(id):
    effect_row = 0
    sql = "delete from posts where id={}".format(id)
    logger.debug(sql)
    db.session.execute(sql)
    db.session.commit()
    if effect_row > 0:
        message = "deleted success id:{}".format(id)
    else:
        message = "id:{} row not found".format(id)
    return {"data": sql, "message": message}, 200
