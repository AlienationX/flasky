# coding=utf-8
# python3

from flask_restful import Resource, reqparse
from flask import request, abort
import pandas as pd
import numpy as np

from app import db
from conf.config import Config
from app.api.auth import auth
from app.common.logger import create_logger
from app.api.utils import UtilityDatetime

logger = create_logger(__name__)


class Apis(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument("offset", type=int, help="Cannot be null")
        parser.add_argument("limit", type=int)
        parser.add_argument("orderby", type=str)
        parser.add_argument("sort", type=str, default="asc", choices=["asc", "desc"])
        parser.add_argument("post_id", type=int)
        self.args = parser.parse_args()
        logger.info(self.args)

    def get(self):
        """获取全部数据"""

        # offset = self.args.get("offset", Config.DEFAULT_OFFSET)  无效，不知道为啥
        offset = self.args.get("offset") or Config.DEFAULT_OFFSET
        limit = self.args.get("limit") or Config.DEFAULT_LIMIT
        post_id = self.args.get("post_id")
        if post_id:
            filter_post_id = "c.post_id={} and".format(post_id)
        else:
            filter_post_id = ""

        sql = """
        select c.id,c.body,c.body_html,c.create_time,c.author_id,u.username as author_name,c.post_id
        from comments c
        left join users u on c.author_id=u.id
        where {filter_post_id} c.disabled=0
        order by create_time desc
        limit {offset},{limit}
        """.format(filter_post_id=filter_post_id, offset=offset, limit=limit)
        logger.debug(sql)
        df = pd.read_sql(sql, con=db.engine)
        df = df.replace({np.nan: None})
        df["create_time"] = df["create_time"].map(UtilityDatetime.format_datetime)

        # data = df.to_json(orient="records")
        data = df.to_dict("records")
        return {"data": data}

    def post(self):
        """插入单条数据"""
        data = request.get_json()
        body = data["body"]
        author_id = data["author_id"]
        post_id = data["post_id"]
        # abort(400)
        sql = "insert into comments (body,author_id,post_id) values ('{}',{},{})".format(body, author_id, post_id)
        logger.debug(sql)
        db.session.execute(sql)
        db.session.commit()
        return {"data": request.json}


class Api(Resource):

    def __init__(self):
        pass

    # def get(self, id):
    #     """获取单条数据"""
    #     sql = """
    #     select c.id,c.body,c.body_html,c.create_time,c.author_id,u.username as author_name,c.post_id
    #     from comments c
    #     left join users u on c.author_id=u.id
    #     where c.id={} and c.disabled=0
    #     """.format(id)
    #     df = pd.read_sql(sql, con=db.engine)
    #     data = df.to_dict("records")
    #     return {"data": data, "message": "OK"}

    def put(self, id):
        """更新单条数据"""
        data = request.get_json()
        body = data["body"]
        disabled = data.get("disabled")
        if disabled:
            disabled_str = ",disabled={}".format(disabled)
        else:
            disabled_str = ""

        sql = "update comments set body='{body}'{disabled_str} where id={id}".format(body=body, disabled_str=disabled_str, id=id)
        logger.debug(sql)
        db.session.execute(sql)
        db.session.commit()
        return {"data": sql}

    def delete(self, id):
        """删除单条数据"""
        effect_row = 0
        sql = "delete from comments where id={}".format(id)
        logger.debug(sql)
        db.session.execute(sql)
        db.session.commit()
        if effect_row > 0:
            message = "deleted success id:{}".format(id)
        else:
            message = "id:{} row not found".format(id)
        return {"data": sql}
