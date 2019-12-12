# coding=utf-8
# python3

from flask import jsonify
from app.api import api


@api.app_errorhandler(404)
def page_not_found():
    response = jsonify({"error": "not found"})
    response.status_code = 404
    return response


@api.app_errorhandler(403)
def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response
