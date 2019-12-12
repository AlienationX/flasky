# coding=utf-8
# python3

from functools import wraps
from flask import g, render_template


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print("This is a decorator: ".format(permission))
            # TODO
            return f(*args, **kwargs)

        return wrapper

    return decorator


def admin_required():
    pass


# def login_required():
#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             if g.user.id == 0:
#                 return render_template("auth/login.html")
#             return f(*args, **kwargs)
#
#         return wrapper
#
#     return decorator


def data_auth_required():
    pass
