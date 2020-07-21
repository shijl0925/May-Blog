#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
from urllib.parse import unquote
import flask
from flask_security import login_required
from flask_babelex import gettext as _
from flask_ckeditor import upload_success, upload_fail
from werkzeug.utils import secure_filename
from app.utils.decorator import permission_required
from app.form.file import UploadForm
from app.form.forms import OperateForm
from app.config import BaseConfig
from app.controller.extensions import csrf


file_bp = flask.Blueprint('files', __name__, url_prefix='/files')


def get_existing_files():
    return [f for f in os.listdir(BaseConfig.FILEUPLOAD_IMG_FOLDER) if "_thumb" not in f]


def get_abs_existing_files():
    return [flask.url_for('files.uploaded_files', filename=f, _external=True) for f in get_existing_files()]


def get_filename(full_file_path):
    return full_file_path.split('/')[-1]


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
        if extension not in flask.current_app.config['FILEUPLOAD_ALLOWED_EXTENSIONS']:
            flask.flash(_("This file extension is not allowed."), category="warning")
            return flask.redirect(flask.url_for("files.upload"))

        if filename in get_existing_files():
            flask.flash(_("File already exists, choose an other name."), category="warning")
            return flask.redirect(flask.url_for("files.upload"))

        file_name = secure_filename(filename)
        file_data.save(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], file_name))

        flask.flash(_("Image saved: ") + filename, category="info")
        return flask.redirect(flask.url_for("files.upload"))

    return flask.render_template("file/upload.html", form=upload_form, delete_form=delete_form)


@file_bp.route('/uploads', methods=["GET", "POST"])
@login_required
@permission_required('ADMINISTER')
def uploads():
    if flask.request.method == "POST":
        for key, f in flask.request.files.items():
            file_name = secure_filename(f.filename)
            f.save(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], file_name))
        return flask.redirect(flask.url_for("files.upload"))


@file_bp.route('/<path:filename>')
def uploaded_files(filename):
    return flask.send_from_directory(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], filename)


@file_bp.route("/delete/<filename>", methods=["POST"])
@login_required
@permission_required('ADMINISTER')
def upload_delete(filename):
    if flask.request.method == "POST":
        filename = unquote(filename)

        if filename not in get_existing_files():
            flask.flash(_("File does not exist!"), category="warning")
            return flask.redirect(flask.url_for("files.upload"))
        else:
            os.remove(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], filename))

            flask.flash(_("Delete Image: ") + filename, category="info")

    return flask.redirect(flask.url_for("files.upload"))


@csrf.exempt
@file_bp.route('/upload', methods=['POST'])
def ckeditor_upload():
    f = flask.request.files.get('upload')

    extension = f.filename.split('.')[-1].lower()
    if extension not in flask.current_app.config['FILEUPLOAD_ALLOWED_EXTENSIONS']:
        return upload_fail(message='Image only!')

    if f.filename in get_existing_files():
        return upload_fail(message='File already exists, choose an other Image!')

    file_name = secure_filename(f.filename)
    f.save(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], file_name))

    url = flask.url_for('files.uploaded_files', filename=file_name)
    return upload_success(url=url)

