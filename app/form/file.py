#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_wtf import FlaskForm
from flask_babelex import lazy_gettext as _
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileField


class UploadForm(FlaskForm):
    upload_name = StringField(
        _('Name'),
        validators=[DataRequired()],
        render_kw={'placeholder': 'jpg, png, jpeg',
                   'class': 'form-control'}
    )
    upload_img = FileField(validators=[FileRequired()])
