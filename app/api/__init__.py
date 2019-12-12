# coding=utf-8
# python3

import os
from flask import Blueprint

api = Blueprint("api", __name__)


# from app.api.resources import posts, comments, users

def import_original_api():
    """动态循环导入，代替import语句：from app.api.resources import posts, comments, users"""
    resources_folder = "resources"
    resources = os.listdir(os.path.join(os.path.dirname(__file__), resources_folder))
    for resource in resources:
        # if resource == "__init__.py" or resource[-3:] != ".py":
        # posts使用flask实现，其他资源使用flask_restful实现
        if resource == "__init__.py" or resource[-3:] != ".py" or resource != "posts.py":
            continue
        else:
            resource = resource[:-3]
        model_str = "{}.{}.{}.{}".format("app", "api", resources_folder, resource)
        print(model_str)
        # model_name = __import__(model_str, globals(), locals(), "Api")
        model_name = __import__(model_str, fromlist=[resource])
        print(model_name)
