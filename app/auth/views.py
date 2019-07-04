# coding=utf-8
# python3

from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.email import send_email
from app.auth import auth
from app.models import User
from app.auth.forms import LoginForm, RegistrationForm
import arrow


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        if user.password_hash and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next_url = request.args.get("next")
            if next_url is None or not next_url.startswith("/"):
                next_url = url_for("main.index")
            return redirect(next_url)
        flash("Invalid username or password")
    return render_template("auth/login.html", form=form)


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
    form = RegistrationForm()
    if form.validate_on_submit():
        db.session.execute(
            "insert into users(username,password,password_hash,email,create_time) values ('{}',{},'{}','{}','{}')".format(
                form.username.data,
                "Null",
                User.generate_hash(form.password.data),
                form.email.data,
                arrow.now().format("YYYY-MM-DD HH:mm:ss")
            )
        )
        db.session.commit()

        # 发送确认邮件
        user = User(email=form.email.data)
        token = user.generate_confirmation_token()
        send_email(user.email, "Confirm Your Account", "auth/email/confirm", user=user, token=token)
        flash("A confirmation email has been sent to you by email.")
        login_user(user)
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Confirm Your Account", "auth/email/confirm", user=current_user, token=token)
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")


@auth.before_app_request
def before_request():
    print("权限请求")
    if current_user.is_authenticated:
        current_user.update_login_time()
        if session.get("is_followings", None) is None:
            session["is_followings"] = 0
        if not current_user.confirmed and request.blueprint != "auth" and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))
    else:
        session["is_followings"] = 0
