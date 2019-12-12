# coding=utf-8
# python3

from flask_restful import Resource, reqparse

from app import db


class Apis(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument("token", type=str, required=True, help="Cannot be null")
        self.args = parser.parse_args()

    def get(self):
        return {"data": "testing..."}


class Api(Resource):
    pass
