#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
import os
import flask
from werkzeug.local import LocalProxy
from app.config import BaseConfig


_datastore = LocalProxy(lambda: flask.current_app.extensions['security'].datastore)

auth_bp = flask.Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/settings/avatars/<path:filename>')
def get_avatar(filename):
    if not os.path.exists(os.path.join(BaseConfig.AVATARS_SAVE_PATH, filename)):
        return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, 'default_avatar.png')
    return flask.send_from_directory(BaseConfig.AVATARS_SAVE_PATH, filename)

