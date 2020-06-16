#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import widgets, StringField, TextAreaField, validators, SubmitField, ValidationError
from app.controller.extensions import db
from app.model.models import Post, Category, Tag


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
    def query_factory(*args):
        return [item.name for item in db.session.query(Category).all()]

    def get_pk(obj):
        return obj

    title = StringField(
        'Title',
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

    abstract = StringField(
        'Abstract',
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

    category = QuerySelectField(
        'Category',
        validators=[validators.DataRequired()],
        render_kw={'class': 'browser-default custom-select'},
        query_factory=query_factory,
        get_pk=get_pk
    )

    tags = QuerySelectMultipleField(
        'Tags',
        validators=[validators.DataRequired()],
        render_kw={'class': 'custom-select'},
        query_factory=tag_choices,
        allow_blank=True,
        get_pk=get_pk
    )

    slug = StringField(
        'Slug',
        validators=[
            validators.DataRequired(),
            validators.Length(1, 256)
        ],
        render_kw={'class': 'form-control'}
    )

    body = CKEditorField(
        'Body',
        validators=[validators.DataRequired()]
    )

    save_submit = SubmitField(
        'Save As Draft',
        render_kw={'class': 'btn btn-blue-grey shadow-none'}
    )

    publish_submit = SubmitField(
        'Publish',
        render_kw={'class': 'btn btn-primary shadow-none'}
    )


class CreateForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            validators.DataRequired(),
            validators.Length(1, 30)
        ],
        render_kw={'class': 'form-control'}
    )