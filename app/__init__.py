# coding=utf-8
# python3

from flask import Flask, request, make_response, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from flask_mail import Mail
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from flask_avatars import Avatars
from flask_restful import Api
from flask_cors import CORS
import arrow
import psutil
import os

from conf.config import config
from app.common.logger import create_logger
from app.api.status import StatusCode

db = SQLAlchemy()
mail = Mail()
socketio = SocketIO()
avatars = Avatars()
cors = CORS()
# restful_api = Api()


login_manager = LoginManager()
login_manager.login_view = "auth.login"

logger = create_logger(__name__)


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    avatars.init_app(app)
    cors.init_app(app)
    # restful_api.init_app(app)  # flask_restful 不支持这样处理？
    restful_api = Api(app)

    # restful api
    restful_api.representations['application/json'] = output_json
    from app.api.routes import init_routers
    init_routers(restful_api)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix="/manage")

    # ??? 为了动态处理 from app.api.resources import posts, comments, users
    from .api import import_original_api
    import_original_api()

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1/resources")

    # 全局的error捕获处理
    @app.before_request
    def before_request():
        """before_request :在请求收到之前绑定一个函数做一些事情。"""
        global before_time
        before_time = arrow.utcnow()
        print("-" * 100)
        logger.info("before request do something...")
        print("request host :", request.remote_addr, request.remote_user)
        print("request url  :", request.url)
        print("current user :", current_user)
        print("request args :", request.args)
        print("request args :", request.args.to_dict())

    @app.after_request
    def after_request(response):
        """after_request: 每一个请求之后绑定一个函数，如果请求没有异常。参数和返回值必须有"""
        logger.info("after request do something...")
        for query in get_debug_queries():
            if query.duration >= app.config["DATABASE_QUERY_TIMEOUT"]:
                logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))

        after_time = arrow.utcnow()
        logger.info("The request spend {} seconds".format((after_time - before_time).seconds))  # 1秒=1000毫秒
        logger.info("The request spend {} milliseconds".format(round((after_time - before_time).microseconds / 1000, 2)))  # 1毫秒=1000微秒
        logger.info("The request spend {} microseconds".format((after_time - before_time).microseconds))  # 微秒
        return response

    @app.teardown_request
    def teardown_request(exception):
        """teardown_request: 每一个请求之后绑定一个函数，即使遇到了异常。"""
        if exception:
            logger.error("app.teardown_request:\n{}".format(exception))
        p1 = psutil.Process(os.getpid())
        print("{:<15} {:.2f}%".format("本机内存占用率:", psutil.virtual_memory().percent))
        print("{:<15} {:.2f}%".format("本机cpu占有率:", psutil.cpu_percent(0)))
        print("{:<15} {:.2f}%".format("该进程内存占用率:", p1.memory_percent()))
        print("{:<15} {:.2f}%".format("该进程cpu占用率:", p1.cpu_percent(None)))
        # logger.info("{:<15} {:.2f}%".format("Native memory footprint:", psutil.virtual_memory().percent))
        # logger.info("{:<15} {:.2f}%".format("Native cpu footprint:", psutil.cpu_percent(0)))
        # logger.info("{:<15} {:.2f}%".format("The process memory footprint:", p1.memory_percent()))
        # logger.info("{:<15} {:.2f}%".format("The process cpu footprint:", p1.cpu_percent(None)))

    @app.errorhandler
    def page_not_found(e):
        print("app.errorhandler: " + e)

    @app.errorhandler(404)
    def page_not_found(e):
        logger.error("@app.errorhandler(404) ========================>".format(e))
        return render_template("404.html")

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        logger.error("@app.errorhandler(500) ========================>".format(e))

    return app


# @restful_api.representation("application/json")
def output_json(data, code, headers=None):
    """restful_api基于返回结果再次封装一层统一的json返回"""
    result = {
        "data": data,
        "status_code": code,
        "message": StatusCode.http_code[code]
    }
    resp = make_response(jsonify(result), code)
    resp.headers.extend(headers or {})
    return resp

# restful api 默认结果为json，如果想支付csv或html，可以单独增加指定输出的格式

# @restful_api.representation('text/html')
# def output_html(data, code, headers=None):
#     resp = make_response(data, code)
#     resp.headers.extend(headers or {})
#     return resp


# @restful_api.representation('text/csv')
# def output_csv(data, code, headers=None):
#     pass
#     # implement csv output!
