#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import re
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
from app.utils.common import resize_image
from app.utils.uploader import Uploader


file_bp = flask.Blueprint('files', __name__, url_prefix='/files')


def get_existing_files():
    return [f for f in os.listdir(BaseConfig.FILEUPLOAD_IMG_FOLDER) if "_s." not in f and "_m." not in f]


def get_abs_existing_files():
    return [flask.url_for('files.uploaded_files', filename=f, _external=True) for f in get_existing_files()]


def get_filename(full_file_path):
    return full_file_path.split('/')[-1]


def get_filename_s(filename):
    filename, ext = os.path.splitext(filename)
    filename += "_s" + ext
    return filename


def get_filename_m(filename):
    filename, ext = os.path.splitext(filename)
    filename += "_m" + ext
    return filename


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

        filename_s = resize_image(file_data, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['small'])
        filename_m = resize_image(file_data, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['medium'])

        flask.flash(_("Image saved: ") + filename, category="info")
        return flask.redirect(flask.url_for("files.upload"))

    return flask.render_template("file/upload.html", form=upload_form, delete_form=delete_form)


@file_bp.route('/uploads', methods=["POST"])
@login_required
@permission_required('ADMINISTER')
def uploads():
    if flask.request.method == "POST":
        for key, f in flask.request.files.items():
            file_name = secure_filename(f.filename)
            f.save(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], file_name))

            filename_s = resize_image(f, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['small'])
            filename_m = resize_image(f, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['medium'])

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

            filename, ext = os.path.splitext(filename)
            filename_s = filename + "_s" + ext
            if filename_s in os.listdir(BaseConfig.FILEUPLOAD_IMG_FOLDER):
                os.remove(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], filename_s))

            filename_m = filename + "_m" + ext
            if filename_m in os.listdir(BaseConfig.FILEUPLOAD_IMG_FOLDER):
                os.remove(os.path.join(flask.current_app.config['FILEUPLOAD_IMG_FOLDER'], filename_m))

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

    filename_s = resize_image(f, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['small'])
    filename_m = resize_image(f, file_name, flask.current_app.config['FILEUPLOAD_IMG_SIZE']['medium'])

    url = flask.url_for('files.uploaded_files', filename=file_name)
    return upload_success(url=url)


@csrf.exempt
@file_bp.route('/ueditor_upload', methods=['GET', 'POST'])
def ueditor_upload():
    mimetype = 'application/json'
    result = {}
    action = flask.request.args.get('action')

    app_abs_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    static_folder = os.path.join(app_abs_folder, "static")

    # 解析JSON格式的配置文件
    with open(os.path.join(static_folder, 'ueditor', 'php',
                           'config.json')) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = flask.json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in flask.request.files:
            field = flask.request.files[fieldName]
            uploader = Uploader(field, config, static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in flask.request.form:
            field = flask.request.form[fieldName]
            uploader = Uploader(field, config, static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in flask.request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in flask.request.form:
            # 而是这个
            source = flask.request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = '请求地址出错'

    result = flask.json.dumps(result)

    if 'callback' in flask.request.args:
        callback = flask.request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = flask.json.dumps({'state': 'callback参数不合法'})

    res = flask.make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res

