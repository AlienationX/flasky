# coding=utf-8
# python3

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    APP_NAME = "Secret"
    TIME_ZONE = "Asia/Shanghai"  # 主要是数据库所在位置的时区
    UPLOAD_FOLDER = os.path.join(basedir, "app/upload")

    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = "lshuwork@163.com"
    MAIL_PASSWORD = "flasky123"  # 邮件账户的密码,这个密码是指的授权码!授权码!授权码! pnTIFA7163
    # MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    APP_MAIL_SUBJECT_PREFIX = "[" + APP_NAME + "]"
    APP_MAIL_SENDER = APP_NAME + " Admin <lshuwork@163.com>"

    # 根据邮箱来判断admin账户
    APP_ADMIN = "lshuwork@163.com"
    # 可以去掉一个警告，具体什么作用还不清楚
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    # 默认值：production
    ENV = "development"
    # 是否开启调试模式  ENV="development" 默认开启
    DEBUG = True
    # 记录模板文件如何载入的调试信息。使用本变量有助于查找为什么模板没有载入 或者载入了错误的模板的原因。
    # EXPLAIN_TEMPLATE_LOADING = True

    # 数据库URL
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/flasky?charset=utf8"
    # 其他数据库链接
    SQLALCHEMY_BINDS = {
        # "impala": "impala://10.15.1.49:25003/default",  # 有很多元数据刷新和缓存的问题，不建议使用
        # "kylin": "kylin://ADMIN:KYLIN@127.0.0.1:7070/learn_kylin?version=v1",
        "mysql": "mysql+pymysql://root:root@127.0.0.1:3306/test?charset=utf8"
    }
    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = False
    # 设置是否在每次连接结束后自动提交数据库中的变动
    SQLALCHEMY_COMMIT_TEARDOWN = True
    # 数据库连接池的大小。默认是数据库引擎的默认值 （通常是 5）
    # SQLALCHEMY_POOL_SIZE = 2


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    # 默认值：production
    # ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
