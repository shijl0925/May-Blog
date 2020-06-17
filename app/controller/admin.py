#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import flask
from redis import Redis
from flask_admin import Admin, expose, AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.menu import MenuLink
from flask_admin.helpers import get_form_data
from flask_security import current_user
from flask_security.utils import encrypt_password
from app.model.models import User, Role, Permission, Settings, Post, Category, Archive, Tag, Relate
from app.controller.extensions import db, avatars
from app.form.auth import CropAvatarForm, UploadAvatarForm
from app.config import BaseConfig
from app.utils.common import remove_preview_avatar
from flask_security.confirmable import generate_confirmation_link
from app.email import send_mail
from app.controller.formaters import _show_avatar, _lock_user, _send_mail, _show_roles, line_formatter
from app.form.forms import CKTextAreaField


class AdminLTEModelView(ModelView):
    list_template = 'flask-admin/model/list.html'
    create_template = 'flask-admin/model/create.html'
    edit_template = 'flask-admin/model/edit.html'
    details_template = 'flask-admin/model/details.html'

    create_modal_template = 'flask-admin/model/modals/create.html'
    edit_modal_template = 'flask-admin/model/modals/edit.html'
    details_modal_template = 'flask-admin/model/modals/details.html'


class AdminLTEFileAdmin(FileAdmin):
    list_template = 'flask-admin/file/list.html'

    upload_template = 'flask-admin/file/form.html'
    mkdir_template = 'flask-admin/file/form.html'
    rename_template = 'flask-admin/file/form.html'
    edit_template = 'flask-admin/file/form.html'

    upload_modal_template = 'flask-admin/file/modals/form.html'
    mkdir_modal_template = 'flask-admin/file/modals/form.html'
    rename_modal_template = 'flask-admin/file/modals/form.html'
    edit_modal_template = 'flask-admin/file/modals/form.html'


class MyAdminIndexView(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if not current_user.is_authenticated:
            return flask.redirect(flask.url_for('security.login', next=flask.request.url))

        if not current_user.is_admin:
            flask.abort(403)

        return self.render('myadmin3/my_index.html')


# Only show the Logout link if the user is logged in.
class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class ProfileView(BaseView):
    @expose('/', methods=["GET", "POST"])
    def index(self):
        upload_form = UploadAvatarForm()
        crop_form = CropAvatarForm()

        if not current_user.is_authenticated:
            return flask.redirect(flask.url_for('security.login', next=flask.request.url))

        if not current_user.is_admin:
            flask.abort(403)

        if flask.request.method == "GET":
            return self.render('myadmin3/user_profile.html', upload_form=upload_form, crop_form=crop_form)
        else:
            data = flask.request.form
            current_user.first_name = data.get('first_name')
            current_user.last_name = data.get('last_name')
            current_user.location = data.get('location')
            current_user.website = data.get('website')
            current_user.bio = data.get('bio')
            db.session.commit()
            return flask.redirect(flask.url_for("profile.index"))

    @expose('/set-password', methods=['POST'])
    def set_password(self):
        data = flask.request.form
        if current_user.validate_password(data.get('old_password')):
            current_user.set_password(data.get('password'))
            db.session.commit()
        else:
            flask.flash('Old password is incorrect.', 'warning')
        return flask.redirect(flask.url_for("profile.index"))

    @expose('/avatar', methods=['GET', 'POST'])
    def change_avatar(self):
        upload_form = UploadAvatarForm()
        crop_form = CropAvatarForm()
        return self.render('myadmin3/change_avatar.html', upload_form=upload_form, crop_form=crop_form)

    @expose('/avatar/upload', methods=['POST'])
    def upload_avatar(self):
        if flask.request.method == "POST":
            data = flask.request.files
            filename = avatars.save_avatar(data.get('image'))
            current_user.avatar_raw = filename
            db.session.commit()
            flask.flash('Image uploaded, please crop.', 'success')
        return flask.redirect(flask.url_for("profile.change_avatar"))

    @expose('/avatar/crop', methods=['POST'])
    def crop_avatar(self):
        if not os.path.exists(os.path.join(BaseConfig.AVATARS_SAVE_PATH, current_user.avatar_raw)):
            flask.flash('Image uploaded failed. Please upload again.', 'warning')
            return flask.redirect(flask.url_for("profile.change_avatar"))

        if flask.request.method == "POST":
            remove_preview_avatar(current_user.avatar_s)
            remove_preview_avatar(current_user.avatar_m)
            remove_preview_avatar(current_user.avatar_l)

            data = flask.request.form
            x = data.get('x')
            y = data.get('y')
            w = data.get('w')
            h = data.get('h')
            filenames = avatars.crop_avatar(current_user.avatar_raw, x, y, w, h)
            current_user.avatar_s = filenames[0]
            current_user.avatar_m = filenames[1]
            current_user.avatar_l = filenames[2]
            db.session.commit()
            flask.flash('Avatar updated.', 'success')

            return flask.redirect(flask.url_for("profile.index"))


class MyBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role('Administrator')

    def inaccessible_callback(self, name, **kwargs):
        """
        根据不同的情况，给予用户不同的提示
        （如未登录用户提示用户需要登录，已登录但非管理员用户提示用户身份错误等)
        :param name:
        :param kwargs:
        :return:
        """
        flask.flash('您没有权限查看该资源', category='danger')
        return flask.redirect(flask.url_for('security.login', next=flask.request.url))


class MyBaseModelview(MyBaseView, AdminLTEModelView):
    page_size = 50  # the number of entries to display on the list view

    can_export = True
    can_view_details = True


class UserBaseModelview(MyBaseModelview):
    @expose("lock", methods=["POST"])
    def lock_user_view(self):
        return_url = self.get_url("user.index_view")
        form = get_form_data()

        if not form:
            flask.flash("Can't get form data.", "error")
            return flask.redirect(return_url)

        uid = form["user_id"]
        user = User.query.get(uid)
        user.lock()

        return flask.redirect(return_url)

    @expose("unlock", methods=["POST"])
    def unlock_user_view(self):
        return_url = self.get_url("user.index_view")
        form = get_form_data()

        if not form:
            flask.flash("Can't get form data.", "error")
            return flask.redirect(return_url)

        uid = form["user_id"]
        user = User.query.get(uid)
        user.unlock()

        return flask.redirect(return_url)

    @expose("send_mail", methods=["POST"])
    def send_mail_view(self):
        return_url = self.get_url("user.index_view")
        form = get_form_data()

        if not form:
            flask.flash("Can't get form data.", "error")
            return flask.redirect(return_url)

        uid = form["user_id"]
        confirmed_user = User.query.get(uid)
        confirmation_link, token = generate_confirmation_link(confirmed_user)

        send_mail(subject="Please confirm your email address",
                  recipient=[confirmed_user.email],
                  template='security/email/confirmation_instructions',
                  user=confirmed_user,
                  confirmation_link=confirmation_link)

        flask.flash("Confirmation instructions have been sent to {}".format(confirmed_user.email), 'success')

        return flask.redirect(return_url)

    edit_modal = True
    create_modal = True
    details_modal = True

    column_exclude_list = ['password']
    column_details_exclude_list = ['password']
    column_export_exclude_list = ['password']
    form_columns = ["username", "roles", "email", "first_name", "last_name", "bio", "website", "location"]

    column_searchable_list = ['first_name', 'last_name', 'email', 'username']
    column_editable_list = ['active', 'first_name', 'last_name']
    column_list = ["avatar", "username", "roles", "email", "first_name", "last_name", "active", "login_count", "send_mail", "lock_user"]

    form_widget_args = {}

    column_formatters = {
        "avatar": _show_avatar,
        "lock_user": _lock_user,
        "send_mail": _send_mail,
        "roles": _show_roles
    }

    column_labels = {
        'email': '邮件',
        'active': '激活',
        'locked': '锁定',
        'first_name': '姓',
        'last_name': '名字',
        'username': '用户名',
        'confirmed_at': '确认',
        'bio': '介绍',
        'website': '网站',
        'location': '地址',
        'password': '密码',
        'roles': '角色',
        'avatar': '头像',
        'avatar_s': '头像(s)',
        'avatar_m': '头像(m)',
        'avatar_l': '头像(l)',
        'avatar_raw': '头像(raw)',
        'last_login_at': '上次登录时间',
        'current_login_at': '当前登录时间',
        'last_login_ip': '上次登录IP',
        'current_login_ip': '当前登录IP',
        'login_count': '登录次数',
        "lock_user": '锁定用户',
        "send_mail": "邮件验证"
    }

    def on_model_change(self, form, model, is_created):
        if is_created is True:
            model.active = True
            model.password = encrypt_password("123456")
            model.generate_avatar()
        super().on_model_change(form, model, is_created)


class RoleBaseModelview(MyBaseModelview):
    column_searchable_list = ['name']
    form_widget_args = {
        "users": {"disabled": True},
    }


class PermissionBaseModelview(MyBaseModelview):
    column_searchable_list = ['name']


class NotificationBaseModelview(MyBaseModelview):
    column_searchable_list = ['message']
    column_formatters = {
        "message": line_formatter,
    }


class PostBaseModelview(MyBaseModelview):
    column_editable_list = ["category", "is_draft"]
    column_exclude_list = ["abstract", "body"]
    form_overrides = {
        'body': CKTextAreaField
    }
    create_template = edit_template = 'myadmin3/ckeditor.html'


class CategoryBaseModelview(MyBaseModelview):
    form_columns = ["name"]


class RelateBaseModelview(MyBaseModelview):
    form_columns = ["name"]


class ArchiveBaseModelview(MyBaseModelview):
    form_columns = ["label"]


class TagBaseModelview(MyBaseModelview):
    form_columns = ["name"]


admin = Admin(
    name='Admin Dashboard',
    base_template='myadmin3/my_master.html',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView(),
    category_icon_classes={
        'Authorization': 'fas fa-users'
})

admin.add_link(MenuLink(name='Back Home', class_name='nav-item', endpoint='posts.posts'))
admin.add_link(LogoutMenuLink(name='Logout', class_name='nav-item', endpoint='security.logout', icon_type=None, icon_value=None))

admin.add_view(ProfileView(name='User Profile',
                           menu_icon_type='fas',
                           menu_icon_value='fa-user',
                           endpoint='profile'))

admin.add_view(UserBaseModelview(User,
                                 db.session,
                                 name='User',
                                 category='Authorization',
                                 endpoint='user'))

admin.add_view(RoleBaseModelview(Role,
                                 db.session,
                                 name='Role',
                                 category='Authorization',
                                 endpoint='role'))

admin.add_view(PermissionBaseModelview(Permission,
                                       db.session,
                                       name='Permission',
                                       category='Authorization',
                                       endpoint='permission'))


admin.add_view(PostBaseModelview(Post,
                                 db.session,
                                 menu_icon_type='fas',
                                 menu_icon_value='fa-clipboard',
                                 name='Posts',
                                 endpoint='post'))


admin.add_view(CategoryBaseModelview(Category,
                                     db.session,
                                     menu_icon_type='fas',
                                     menu_icon_value='fa-star',
                                     name='Category',
                                     endpoint='category'))


admin.add_view(RelateBaseModelview(Relate,
                                   db.session,
                                   menu_icon_type='fas',
                                   menu_icon_value='fa-network-wired',
                                   name='Relate',
                                   endpoint='relate'))


admin.add_view(TagBaseModelview(Tag,
                                db.session,
                                menu_icon_type='fas',
                                menu_icon_value='fa-tags',
                                name='Tag',
                                endpoint='tag'))


admin.add_view(ArchiveBaseModelview(Archive,
                                    db.session,
                                    menu_icon_type='fas',
                                    menu_icon_value='fa-archive',
                                    name='Archive',
                                    endpoint='archive'))


admin.add_view(MyBaseModelview(Settings,
                               db.session,
                               menu_icon_type='fas',
                               menu_icon_value='fa-cogs',
                               name='Settings',
                               endpoint='settings'))


class MyFileAdmin(MyBaseView, AdminLTEFileAdmin):
    editable_extensions = ('md', 'txt', 'html')


# log_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
# admin.add_view(MyFileAdmin(log_path, '/log/', name='Log Files', menu_icon_type='fas', menu_icon_value='fa-copy'))

static_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
admin.add_view(MyFileAdmin(static_path, name='Static Files', menu_icon_type='fas', menu_icon_value='fa-copy'))
