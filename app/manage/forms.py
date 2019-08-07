# coding=utf-8
# python3

from flask_wtf import FlaskForm
from wtforms import SubmitField


class UploadForm(FlaskForm):
    submit = SubmitField()


class DownloadForm(FlaskForm):
    pass
