# coding=utf-8
# python3

from flask import render_template, redirect, url_for, request, current_app, flash
from app.manage import manage
from app import db
from flask_login import current_user, login_required
import pandas as pd
import os


@manage.route("/")
@login_required
def index():
    return render_template("manage/index.html")


@manage.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("excel")
        filename = file.filename
        allowed_extensions = ["xls", "xlsx"]
        if "." in filename and filename.split(".")[-1] in allowed_extensions:
            df = pd.read_excel(file)
            df.to_sql("t_excel", con=db.engine, index=False, if_exists="append", chunksize=1000)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], "{}-{}".format(current_user.username, filename)))
            flash("Upload success.")
        else:
            flash("File type error, must be xls or xlsx.")
        # return redirect(url_for("manage.upload"))
    return render_template("manage/upload.html")


@manage.route("/download", methods=["GET", "POST"])
@login_required
def download():
    return render_template("manage/download.html")
