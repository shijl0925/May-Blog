import os
import flask
from sqlalchemy import func
from datetime import datetime
from flask_wtf.csrf import CSRFError
from flask_security import current_user
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
    mdb,
    boostrap,
    ckeditor,
    csrf,
    whooshee
)
from app.controller.admin import admin
from app.view import init_blue_print
from app.controller.security import create_security
from app.controller.request import save_request
from app.model.models import User, Post, Category, Tag, Archive
from app.view.file import get_abs_existing_files, get_filename

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


def inject_context_variables():
    admin = User.query.get(1)
    categories = Category.query.all()
    archives = Archive.query.all()
    tags = Tag.query.all()

    post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).scalar()
    draft_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=True).scalar()

    category_nums = db.session.query(func.count(Category.id)).scalar()
    tag_nums = db.session.query(func.count(Tag.id)).scalar()

    latest_posts = Post.query.filter_by(is_draft=False).order_by(Post.timestamp.desc()).limit(3).all()
    older_posts = Post.query.filter_by(is_draft=False).order_by(Post.timestamp).limit(3).all()
    popular_posts = Post.query.filter_by(is_draft=False).order_by(Post.visit_count.desc()).limit(6).all()

    return dict(
        admin=admin,
        post_nums=post_nums,
        draft_nums=draft_nums,
        categories=categories,
        tags=tags,
        archives=archives,
        category_nums=category_nums,
        tag_nums=tag_nums,
        latest_posts=latest_posts,
        older_posts=older_posts,
        popular_posts=popular_posts
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
        archive=search_archive).scalar()
    return post_nums


def format_date(str):
    return datetime.strptime(str, "%Y/%m").strftime("%b.%Y")


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
    # toolbar.init_app(app_)
    moment.init_app(app_)
    admin.init_app(app_)
    adminlte.init_app(app_)
    babel.init_app(app_)
    avatars.init_app(app_)
    ckeditor.init_app(app_)
    whooshee.init_app(app_)
    csrf.init_app(app_)

    # app_.after_request(save_request)

    app_.context_processor(inject_context_variables)
    app_.add_template_global(get_abs_existing_files, "get_abs_existing_files")
    app_.add_template_filter(get_filename, "get_filename")

    app_.add_template_filter(count_post_nums_with_tag, 'count_post_nums_with_tag')
    app_.add_template_filter(count_post_nums_with_category, 'count_post_nums_with_category')
    app_.add_template_filter(count_post_nums_with_archive, 'count_post_nums_with_archive')

    app_.add_template_filter(format_date, 'format_date')

    app_.jinja_env.trim_blocks = True
    app_.jinja_env.lstrip_blocks = True

    init_blue_print(app_)
    register_errorhandlers(app_)

    security = create_security(app_)

    return app_


app = create_app("development")
