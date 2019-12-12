# coding=utf-8
# python3

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_httpauth import HTTPBasicAuth
from flask import g, request

from app import db
from app.models import User
from conf.config import Config

auth = HTTPBasicAuth()

"""
@auth.verify_password 功能会覆盖掉 @auth.get_password
@auth.get_password 不建议使用，直接修改 @auth.verify_password 即可
"""


# @auth.get_password
# def get_password(username):
#     if username == 'test':
#         return 'test123'
#     return None


def verify_token(token):
    s = Serializer(Config.SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        # token正确但是过期了，刷新或登陆重新获取
        return False
    except BadSignature:
        # token错误
        return False

    user = db.engine.execute("select 1 from users t where t.id={} limit 1".format(data.get("id")))
    if user.rowcount == 0:
        return False
    else:
        return True


@auth.verify_password
def verify_password(username_or_token, password):
    if verify_token(username_or_token):
        return True
    else:
        user = User(username=username_or_token)
        if user.verify_password(password):
            g.user = user
            return True
        else:
            return False


@auth.error_handler
def unauthorized():
    # 401使用浏览器访问，会弹出用户名和密码的对话框，建议使用403
    return {'error': 'Unauthorized access'}, 401
