#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_wtf import FlaskForm
from flask_babelex import lazy_gettext as _
from wtforms import StringField, SubmitField, PasswordField, BooleanField, validators, ValidationError, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_security.forms import (
    Required,
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ConfirmRegisterForm,
    SendConfirmationForm,
    ResetPasswordForm,
    email_required,
    email_validator,
    valid_user_email,
    unique_user_email,
    password_required,
    password_length
)
from app.model.models import User


class CustomLoginForm(LoginForm):
    email = StringField(_('Email Address'),
                        validators=[Required(message='EMAIL_NOT_PROVIDED')])
    password = PasswordField(_('Password'),
                             validators=[password_required])
    remember = BooleanField(_('Remember Me'))
    submit = SubmitField(_('Login'),
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomForgotPasswordForm(ForgotPasswordForm):
    email = StringField(_('Email Address'),
                        validators=[email_required, email_validator, valid_user_email])
    submit = SubmitField(_('Recover Password'),
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomConfirmRegisterForm(ConfirmRegisterForm):
    email = StringField(_('Email Address'),
                        validators=[email_required, email_validator, unique_user_email])
    username = StringField(_('User Name'),
                           validators=[Required()])
    first_name = StringField(_('First Name'),
                             validators=[Required()])
    last_name = StringField(_('Last Name'),
                            validators=[Required()])
    password = PasswordField(_('Password'),
                             validators=[password_required, password_length])

    submit = SubmitField(_('Register'), render_kw={'class': 'btn btn-primary btn-block',
                                                   'style': 'width: 320px;'})


class CustomRegisterForm(CustomConfirmRegisterForm, RegisterForm):
    password_confirm = PasswordField(_('Confirm Password'),
                                     validators=[validators.EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                                                 password_required])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class CustomSendConfirmationForm(SendConfirmationForm):
    email = StringField(_('Email Address'),
                        validators=[email_required, email_validator, valid_user_email])
    submit = SubmitField(_('Resend Confirmation Instructions'),
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomResetPasswordForm(ResetPasswordForm):
    submit = SubmitField(_('Reset Password'),
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class EditProfileForm(FlaskForm):
    username = StringField(label=_('User Name'),
                           validators=[DataRequired()],
                           render_kw={'class': 'form-control form-control-sm'})

    email = StringField(label=_('Email Address'),
                        validators=[DataRequired(), Length(1, 64)],
                        render_kw={'class': 'form-control form-control-sm'})

    first_name = StringField(label=_('First Name'),
                             validators=[DataRequired()],
                             render_kw={'class': 'form-control form-control-sm'})

    last_name = StringField(label=_('Last Name'),
                            validators=[DataRequired()],
                            render_kw={'class': 'form-control form-control-sm'})

    location = StringField(label=_('Address'),
                           validators=[DataRequired()],
                           render_kw={'class': 'form-control form-control-sm'})

    website = StringField(label=_('Website'),
                          validators=[DataRequired()],
                          render_kw={'class': 'form-control form-control-sm'})

    bio = TextAreaField(label=_('About me'),
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Basic textarea',
                                   'class': 'form-control md-textarea'})

    submit = SubmitField(_('Submit'), render_kw={'class': 'btn btn-primary btn-block'})


class UploadForm(FlaskForm):
    image = FileField(_('Upload your file'),
                      validators=[
                          FileRequired(),
                          FileAllowed(
                              ['jpg', 'png', 'jpeg'], 'The file format should be .jpg or .png or jpeg.')]
                      )
    submit = SubmitField(_('Upload'), render_kw={'class': 'btn btn-primary btn-md'})


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField(_('Crop'), render_kw={'class': 'btn btn-primary btn-md'})


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(_('Old Password'),
                                 validators=[DataRequired()],
                                 render_kw={'class': 'form-control'})
    password = PasswordField(_('New Password'),
                             validators=[DataRequired(), Length(8, 128), EqualTo('password2')],
                             render_kw={'class': 'form-control'})
    password2 = PasswordField(_('Confirm Password'),
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control'})
    submit = SubmitField(render_kw={'class': 'btn btn-primary btn-md'})
