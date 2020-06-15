#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from flask_security import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from app.controller.extensions import db
from app.form.auth import (
    CustomLoginForm,
    CustomRegisterForm,
    CustomForgotPasswordForm,
    CustomConfirmRegisterForm,
    CustomSendConfirmationForm,
    CustomResetPasswordForm
)
from app.model.models import User, Role
from app.config import security_messages
from flask_security import AnonymousUser


class Guest(AnonymousUser):
    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False


def SetSecurityMessagesConfig(app, messages):
    for key, value in messages.items():
        app.config[key] = value
    return app


# Setup Flask-Security
def create_security(app):
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    SetSecurityMessagesConfig(app, security_messages)
    security = Security(app,
                        user_datastore,
                        login_form=CustomLoginForm,
                        confirm_register_form=CustomConfirmRegisterForm,
                        register_form=CustomRegisterForm,
                        forgot_password_form=CustomForgotPasswordForm,
                        send_confirmation_form=CustomSendConfirmationForm,
                        reset_password_form=CustomResetPasswordForm,
                        anonymous_user=Guest)
    return security
