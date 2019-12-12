# coding=utf-8
# python3

import os

from conf.config import Config
from app.common.logger import create_logger

logger = create_logger(__name__)


def init_routers(api):
    """动态循环导入api，文件路径为url"""
    current_path = os.path.dirname(__file__)
    api_files = []
    for path, folders, files in os.walk(current_path):
        if os.path.basename(path) in ("books", "resources"):
            path_part = "/".join(path.split(os.sep)[-3:])
            for file in files:
                if file == "__init__.py" or file[-3:] != ".py" or file == "posts.py":
                    continue
                api_files.append(path_part + "/" + file[:-3])
        else:
            continue

    print(api_files)
    for api_file in api_files:
        model_str = api_file.replace("/", ".")
        folder = api_file.split("/")[-2:-1][0]  # list双参数切片还是个list，所以需要再次定位
        resource = api_file.split("/")[-1]
        logger.info(model_str)
        # model_name = __import__(model_str, globals(), locals(), "Api")
        model_name = __import__(model_str, fromlist=[resource])
        url_name = "/api/v1/{folder}/{resource}".format(folder=folder, resource=resource)
        class_name = resource.capitalize()
        print(model_name, url_name, class_name)
        # 还需要添加 url post/<int:id>
        # api.add_resource(model_name.Api, url_name, endpoint=class_name)
        api.add_resource(model_name.Apis, url_name, endpoint=class_name)

