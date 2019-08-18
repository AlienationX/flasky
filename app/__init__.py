# coding=utf-8
# python3

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from flask_avatars import Avatars
from flask_ckeditor import CKEditor
from config import config
from app.common.logger import create_logger
import arrow
import psutil
import os

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
socketio = SocketIO()
avatars = Avatars()
ckeditor = CKEditor()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

logger = create_logger(__name__)


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    avatars.init_app(app)
    ckeditor.init_app(app)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix="/manage")

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    # 全局的error捕获处理
    @app.before_request
    def before_request():
        """before_request :在请求收到之前绑定一个函数做一些事情。"""
        global before_time
        before_time = arrow.utcnow()
        print("-" * 100)
        logger.info("before request do something...")
        print(request.url)
        print(current_user)
        print(request.args)
        print(request.args.to_dict())

    @app.after_request
    def after_request(response):
        """after_request: 每一个请求之后绑定一个函数，如果请求没有异常。参数和返回值必须有"""
        logger.info("after request do something...")
        after_time = arrow.utcnow()
        print("The request spend {} seconds".format((after_time - before_time).seconds))  # 1秒=1000毫秒
        print("The request spend {} milliseconds".format((after_time - before_time).microseconds))  # 1毫秒=1000微秒
        print("-" * 100)
        return response

    @app.teardown_request
    def teardown_request(exception):
        """teardown_request: 每一个请求之后绑定一个函数，即使遇到了异常。"""
        if exception:
            print(exception)
        p1 = psutil.Process(os.getpid())
        print('本机内存占用率:%.2f%%' % (psutil.virtual_memory().percent))
        print('本机cpu占有率:%.2f%%' % (psutil.cpu_percent(0)))
        print('该进程内存占用率:%.2f%%' % (p1.memory_percent()))
        print('该进程cpu占有率:%.2f%%' % (p1.cpu_percent(None)))

    @app.errorhandler
    def page_not_found(e):
        print("error: " + e)

    # @app.errorhandler(404)
    # def page_not_found(e):
    #     print(e)
    #     return render_template("404.html")

    return app
