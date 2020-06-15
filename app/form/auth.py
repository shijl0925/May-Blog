#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_wtf import FlaskForm
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
    email = StringField('Email Address',
                        validators=[Required(message='EMAIL_NOT_PROVIDED')])
    password = PasswordField('Password',
                             validators=[password_required])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login',
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomForgotPasswordForm(ForgotPasswordForm):
    email = StringField('Email Address',
                        validators=[email_required, email_validator, valid_user_email])
    submit = SubmitField('Recover Password',
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomConfirmRegisterForm(ConfirmRegisterForm):
    email = StringField('Email',
                        validators=[email_required, email_validator, unique_user_email])
    username = StringField('User Name',
                           validators=[Required()])
    first_name = StringField('First Name',
                             validators=[Required()])
    last_name = StringField('Last Name',
                            validators=[Required()])
    password = PasswordField('Password',
                             validators=[password_required, password_length])

    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary btn-block',
                                                'style': 'width: 320px;'})


class CustomRegisterForm(CustomConfirmRegisterForm, RegisterForm):
    password_confirm = PasswordField('Confirm Password',
                                     validators=[validators.EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                                                 password_required])

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class CustomSendConfirmationForm(SendConfirmationForm):
    email = StringField('Email Address',
                        validators=[email_required, email_validator, valid_user_email])
    submit = SubmitField('Resend Confirmation Instructions',
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class CustomResetPasswordForm(ResetPasswordForm):
    submit = SubmitField('Reset Password',
                         render_kw={'class': 'btn btn-primary btn-block',
                                    'style': 'width: 320px;'})


class EditProfileForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired()],
                           render_kw={'class': 'form-control form-control-sm'})

    email = StringField(label='Email Address',
                        validators=[DataRequired(), Length(1, 64)],
                        render_kw={'class': 'form-control form-control-sm'})

    first_name = StringField(label='First Name',
                             validators=[DataRequired()],
                             render_kw={'class': 'form-control form-control-sm'})

    last_name = StringField(label='Last Name',
                            validators=[DataRequired()],
                            render_kw={'class': 'form-control form-control-sm'})

    location = StringField(label='Address',
                           validators=[DataRequired()],
                           render_kw={'class': 'form-control form-control-sm'})

    website = StringField(label='Website',
                          validators=[DataRequired()],
                          render_kw={'class': 'form-control form-control-sm'})

    bio = TextAreaField(label='About me',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Basic textarea',
                                   'class': 'form-control md-textarea'})

    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary btn-block'})


class UploadAvatarForm(FlaskForm):
    image = FileField('Upload your file',
                      validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'The file format should be .jpg or .png.')])
    submit = SubmitField('Upload', render_kw={'class': 'btn btn-primary btn-md'})


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('Crop', render_kw={'class': 'btn btn-primary btn-md'})


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',
                                 validators=[DataRequired()],
                                 render_kw={'class': 'form-control'})
    password = PasswordField('New Password',
                             validators=[DataRequired(), Length(8, 128), EqualTo('password2')],
                             render_kw={'class': 'form-control'})
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control'})
    submit = SubmitField(render_kw={'class': 'btn btn-primary btn-md'})
