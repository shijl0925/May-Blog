#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_wtf import FlaskForm
from flask_babelex import lazy_gettext as _
from flask_ckeditor import CKEditorField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import widgets, StringField, TextAreaField, validators, SubmitField, ValidationError, BooleanField
from app.controller.extensions import db
from app.model.models import Post, Category, Tag, Collection


class OperateForm(FlaskForm):
    pass


class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        # add WYSIWYG class to existing classes
        existing_classes = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = '{} {}'.format(existing_classes, "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class SearchForm(FlaskForm):
    q = StringField(
        label='Search',
        validators=[validators.DataRequired()],
        render_kw={
            'placeholder': 'Search',
            'class': 'form-control form-control-sm mr-3 w-75'
        }
    )


def tag_choices():
    return [item.name for item in db.session.query(Tag).all()]


class PostForm(FlaskForm):
    def query_category_factory(*args):
        return [item.name for item in db.session.query(Category).all()]

    def query_collection_factory(*args):
        return [""] + [item.name for item in db.session.query(Collection).all()]

    def get_pk(obj):
        return obj

    title = StringField(
        _('Title'),
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

    background_image_url = StringField(
        _('Background Image Url'),
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

    category = QuerySelectField(
        _('Category'),
        validators=[validators.DataRequired()],
        render_kw={'class': 'browser-default custom-select'},
        query_factory=query_category_factory,
        get_pk=get_pk
    )

    collection = QuerySelectField(
        _('Topic'),
        render_kw={'class': 'browser-default custom-select'},
        query_factory=query_collection_factory,
        get_pk=get_pk
    )

    tags = QuerySelectMultipleField(
        _('Tags'),
        validators=[validators.DataRequired()],
        render_kw={'class': 'custom-select'},
        query_factory=tag_choices,
        allow_blank=True,
        get_pk=get_pk
    )

    body = TextAreaField(
        _('Body'),
        render_kw={'placeholder': 'Basic textarea',
                   'class': 'form-control md-textarea'}
    )

    deny_comment = BooleanField(_('Deny Comment'))
    privacy = BooleanField(_('Set Private'))

    is_markdown = BooleanField(_('Markdown'))

    save_submit = SubmitField(
        _('Save As Draft'),
        render_kw={'class': 'btn btn-blue-grey shadow-none'}
    )

    publish_submit = SubmitField(
        _('Publish'),
        render_kw={'class': 'btn btn-primary shadow-none'}
    )


class CreateForm(FlaskForm):
    name = StringField(
        _('Name'),
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )


class CreateTopicForm(CreateForm):
    description = StringField(
        _('Description'),
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )
    background = StringField(
        _('Background'),
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

