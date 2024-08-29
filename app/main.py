import os
import flask
from sqlalchemy import func
from datetime import datetime
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError
from app.utils import config_log, get_abs_dir
from app.config import config
from app.controller.extensions import (
    mail,
    toolbar,
    db,
    moment,
    babel,
    avatars,
    adminlte,
    ckeditor,
    dropzone,
    csrf,
    whooshee,
    jwt
)
from app.controller.commands import initdb
from app.controller.admin import admin
from app.view import init_blue_print
from app.controller.security import create_security
from app.controller.request import save_request
from app.model.models import User, Post, Category, Tag, Archive, Link
from app.controller.jwt import (
    my_user_loader_callback,
    my_expired_token_callback,
    my_invalid_token_callback,
    my_unauthorized_token_callback
)
from app.view.file import (
    get_abs_existing_files,
    get_filename,
    get_filename_s,
    get_filename_m
)

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


def add_template_filters(app):
    app.add_template_filter(get_filename, "file_name")
    app.add_template_filter(get_filename_m, "filename_m")
    app.add_template_filter(get_filename_s, "filename_s")

    app.add_template_filter(count_post_nums_with_tag, 'count_post_nums_with_tag')
    app.add_template_filter(count_post_nums_with_category, 'count_post_nums_with_category')
    app.add_template_filter(count_post_nums_with_archive, 'count_post_nums_with_archive')
    app.add_template_filter(count_post_nums_with_topic, 'count_post_nums_with_topic')

    app.add_template_filter(format_date, 'format_date')


def register_commands(app):
    """Register Click commands."""
    commands = [initdb]
    for command in commands:
        app.cli.add_command(command)


def init_jwt():
    jwt.user_loader_callback_loader(my_user_loader_callback)
    jwt.expired_token_loader(my_expired_token_callback)
    jwt.invalid_token_loader(my_invalid_token_callback)
    jwt.unauthorized_loader(my_unauthorized_token_callback)


def register_extensions(app):
    mail.init_app(app)
    db.init_app(app)
    if app.config['DEBUG']:
        toolbar.init_app(app)
    moment.init_app(app)
    admin.init_app(app)
    adminlte.init_app(app)
    babel.init_app(app)
    avatars.init_app(app)
    ckeditor.init_app(app)
    dropzone.init_app(app)
    whooshee.init_app(app)
    csrf.init_app(app)
    jwt.init_app(app)


def inject_context_variables():
    admin = User.query.first()
    categories = Category.query.all()
    archives = Archive.query.all()
    tags = Tag.query.all()
    links = Link.query.all()

    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).scalar()
    draft_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=True).scalar()

    category_nums = db.session.query(func.count(Category.id)).scalar()
    tag_nums = db.session.query(func.count(Tag.id)).scalar()

    latest_posts = Post.query.filter_by(is_draft=False).order_by(Post.timestamp.desc()).limit(3).all()
    older_posts = Post.query.filter_by(is_draft=False).order_by(Post.timestamp).limit(3).all()
    popular_posts = Post.query.filter_by(is_draft=False).order_by(Post.visit_count.desc()).limit(6).all()

    now = datetime.now()
    weekday = now.isoweekday()

    return dict(
        admin=admin,
        post_nums=post_nums,
        draft_nums=draft_nums,
        categories=categories,
        tags=tags,
        links=links,
        archives=archives,
        category_nums=category_nums,
        tag_nums=tag_nums,
        latest_posts=latest_posts,
        older_posts=older_posts,
        popular_posts=popular_posts,
        weekday=weekday
    )


def count_post_nums_with_tag(search_tag):
    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).filter(
        Post.tags.contains(search_tag)).scalar()
    return post_nums


def count_post_nums_with_category(search_category):
    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).filter_by(
        category=search_category).scalar()
    return post_nums


def count_post_nums_with_archive(search_archive):
    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).filter_by(
        archive_id=search_archive.id).scalar()
    return post_nums


def count_post_nums_with_topic(search_topic):
    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).filter_by(
        collection=search_topic).scalar()
    return post_nums


def format_date(str):
    return datetime.strptime(str, "%Y/%m").strftime("%b.%Y")


def create_app(env=None):
    # config_log()
    app_ = flask.Flask(
        __name__,
        template_folder=os.path.join(apps_abs_dir, 'templates'),
        static_folder=os.path.join(apps_abs_dir, 'static')
    )
    if env is None:
        env = os.environ.get('FLASK_ENV', 'default')
    app_.config.from_object(config.get(env))

    init_jwt()
    register_extensions(app_)
    register_commands(app_)

    if app_.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite:"):
        Migrate(app_, db, render_as_batch=True)
    else:
        Migrate(app_, db)

    # app_.after_request(save_request)

    app_.context_processor(inject_context_variables)
    app_.add_template_global(get_abs_existing_files, "get_abs_existing_files")
    add_template_filters(app_)

    app_.jinja_env.trim_blocks = True
    app_.jinja_env.lstrip_blocks = True
    app_.jinja_env.add_extension('jinja2.ext.do')

    init_blue_print(app_)
    register_errorhandlers(app_)

    security = create_security(app_)

    return app_


app = create_app("development")
