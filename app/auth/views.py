# coding=utf-8
# python3

from flask import render_template, flash, redirect, url_for, request, session, g, make_response
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.email import send_email
from app.auth import auth
from app.models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember_me = request.form.get("rememeber_me")
        user = User(email=email)
        if user.password_hash and user.verify_password(password):
            login_user(user, remember_me)
            next_url = request.args.get("next")
            if next_url is None or not next_url.startswith("/"):
                next_url = url_for("main.index")
            # return redirect(next_url)
            resp = make_response(redirect(next_url))
            token = user.generate_token(expiration=2 * 24 * 60 * 60)
            resp.set_cookie("code", token, max_age=2 * 24 * 60 * 60)
            resp.set_cookie("remember_me", str(remember_me), max_age=7 * 24 * 60 * 60)
            resp.set_cookie("version", "web_v0.1", max_age=30 * 24 * 60 * 60)
            return resp
        flash("Invalid username or password")
    return render_template("auth/login.html")


@auth.route("/change_password")
@login_required
def change_password():
    return "change_password"


@auth.route("/change_email")
@login_required
def change_email():
    return "change_email"


@auth.route("/reset_password")
@login_required
def reset_password():
    return "reset_password"


@auth.route("/logout")
@login_required
def logout():
    session["is_followings"] = 0
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        sql = "select email from users where email='{}' limit 1".format(email)
        if db.session.execute(sql).fetchall():
            flash("The email already exists.")
            return render_template("auth/register.html")

        db.session.execute(
            "insert into users(username,password,password_hash,email,email_hash) values ('{}',{},'{}','{}')".format(
                username,
                "Null",
                User.generate_hash(password),
                email,
                User.generate_hash(email)
            )
        )
        db.session.commit()

        # 发送确认邮件
        user = User(email=email)
        token = user.generate_token()
        send_email(user.email, "Confirm Your Account", "auth/email/verify_token", user=user, token=token)
        login_user(user)
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html")


@auth.route("/verify_token")
@login_required
def resend_confirmation():
    token = g.user.generate_token()
    send_email(g.user.email, "Confirm Your Account", "auth/email/verify_token", user=g.user, token=token)
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/verify_token/<token>")
@login_required
def confirm(token):
    if g.user.confirmed:
        return redirect(url_for("main.index"))
    if g.user.update_confirmed(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/unconfirmed")
def unconfirmed():
    if g.user.is_anonymous or g.user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.before_app_request
def before_request():
    print("auth/views.py before_app_request 权限请求")
    if current_user.is_authenticated:
        if session.get("is_followings", None) is None:
            session["is_followings"] = 0
        if not current_user.confirmed and request.blueprint != "auth" and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))
    else:
        session["is_followings"] = 0
