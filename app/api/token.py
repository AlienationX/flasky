# coding=utf-8
# python3


from app.api import api
from app.api.auth import auth
from flask import g


@api.route("/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_token()
    return {'token': token.decode('ascii')}


def refresh_auth_token():
    pass
