import os
import flask
from flask_wtf.csrf import CSRFError
from app.utils import config_log, get_abs_dir
from app.config import config
from app.controller.extensions import mail, toolbar, db, moment, babel, avatars, adminlte, mdb, boostrap, ckeditor, csrf
from app.controller.admin import admin
from app.view import init_blue_print
from app.controller.security import create_security
from app.controller.request import save_request

apps_abs_dir = get_abs_dir(__file__)


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return flask.render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return flask.render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return flask.render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return flask.render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return flask.render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return flask.render_template('errors/400.html', description=e.description), 400


@babel.localeselector
def get_locale():
    return flask.request.accept_languages.best_match(['zh', 'en'])


def create_app(env=None):
    config_log()
    app_ = flask.Flask(
        __name__,
        template_folder=os.path.join(apps_abs_dir, 'templates'),
        static_folder=os.path.join(apps_abs_dir, 'static')
    )
    if env is None:
        env = os.environ.get('FLASK_ENV', 'default')
    app_.config.from_object(config.get(env))

    boostrap.init_app(app_)
    mdb.init_app(app_)
    mail.init_app(app_)
    db.init_app(app_)
    toolbar.init_app(app_)
    moment.init_app(app_)
    admin.init_app(app_)
    adminlte.init_app(app_)
    babel.init_app(app_)
    avatars.init_app(app_)
    ckeditor.init_app(app_)
    csrf.init_app(app_)

    # app_.after_request(save_request)

    app_.jinja_env.trim_blocks = True
    app_.jinja_env.lstrip_blocks = True

    init_blue_print(app_)
    register_errorhandlers(app_)

    security = create_security(app_)

    return app_


app = create_app()
