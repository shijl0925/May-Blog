#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import flask
from flask_security import login_required
from app.utils.decorator import permission_required
from app.form.file import UploadForm
from app.form.forms import OperateForm
from app.config import BaseConfig


file_bp = flask.Blueprint('files', __name__, url_prefix='/files')

abs_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
img_folder = BaseConfig.FILEUPLOAD_IMG_FOLDER
img_folder = img_folder if img_folder.endswith("/") else img_folder + "/"


def get_existing_files():
    abs_img_folder = os.path.join(abs_dir, "static", img_folder)
    return [f for f in os.listdir(abs_img_folder)]


def get_base_path():
    return flask.url_for("static", filename=img_folder)


def get_abs_existing_files():
    return [get_base_path() + f for f in get_existing_files()]


def get_filename(full_file_path):
    return full_file_path[full_file_path.rfind("/") + 1:]


@file_bp.route('/', methods=["GET", "POST"])
@login_required
@permission_required('ADMINISTER')
def upload():
    upload_form = UploadForm()
    delete_form = OperateForm()
    if upload_form.validate_on_submit():
        filename = upload_form.upload_name.data
        file_data = flask.request.files.get('upload_img')
        extension = filename.split('.')[-1].lower()

        if extension not in BaseConfig.FILEUPLOAD_ALLOWED_EXTENSIONS:
            flask.flash("This file extension is not allowed.", category="warning")
            return flask.redirect(flask.url_for("files.upload"))

        if filename in get_existing_files():
            flask.flash("File already exists, choose an other name.", category="warning")
            return flask.redirect(flask.url_for("files.upload"))

        abs_img_folder = os.path.join(abs_dir, "static", img_folder)
        file_data.save(os.path.join(abs_img_folder, filename))

        flask.flash("Image saved: " + filename, category="info")
        return flask.redirect(flask.url_for("files.upload"))

    return flask.render_template("file/upload.html", form=upload_form, delete_form=delete_form)


@file_bp.route("/delete/<filename>", methods=["POST"])
@login_required
@permission_required('ADMINISTER')
def upload_delete(filename):
    if flask.request.method == "POST":
        abs_img_folder = os.path.join(abs_dir, "static", img_folder)
        if filename not in get_existing_files():
            flask.flash("File does not exist!", category="warning")
            return flask.redirect(flask.url_for("files.upload"))
        else:
            os.remove(os.path.join(abs_img_folder, filename))
            flask.flash("Delete Image " + filename, category="info")

    return flask.redirect(flask.url_for("files.upload"))

