from datetime import datetime
import flask
from flask_security import login_required, current_user
from sqlalchemy import or_
from slugify import slugify
from flask_babelex import gettext as _
from app.model.models import Post, Category, Tag, Archive, Collection, Comment
from app.form.forms import PostForm, OperateForm, CreateForm
from app.controller.extensions import db
from app.utils.common import redirect_back
from app.utils.decorator import permission_required
from app.controller.signals import post_visited
from app.controller.md_ext import md

posts_bp = flask.Blueprint('posts', __name__, url_prefix='/')


@posts_bp.route('/', methods=['GET'])
def posts():
    now = datetime.now()
    weekday = now.isoweekday()

    page = int(flask.request.args.get('page', 1))
    category = flask.request.args.get('category', '')
    tag = flask.request.args.get('tag', '')
    archive = flask.request.args.get('archive', '')

    posts = Post.query.filter_by(is_draft=False)

    if category:
        search_category = Category.query.filter_by(name=category).first_or_404()
        posts = posts.filter_by(category=search_category)

    if tag:
        search_tag = Tag.query.filter_by(name=tag).first_or_404()
        posts = posts.filter(Post.tags.contains(search_tag))

    if archive:
        search_archive = Archive.query.filter_by(label=archive).first_or_404()
        posts = posts.filter_by(archive=search_archive)

    pagination = posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=10)

    if pagination.page == 1:
        posts_template = "index.html"
    else:
        posts_template = "posts.html"

    return flask.render_template(
        posts_template,
        pagination=pagination,
        posts=pagination.items,
        weekday=weekday
    )


@posts_bp.route('/archives', methods=['GET'])
def archives():
    page = int(flask.request.args.get('page', 1))
    pagination = Archive.query.paginate(page=page, per_page=5)
    return flask.render_template(
        "archive.html",
        pagination=pagination,
        archives=pagination.items
    )


@posts_bp.route('/drafts', methods=['GET'])
@login_required
@permission_required('ADMINISTER')
def draft():
    operate_form = OperateForm()
    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=True).order_by(Post.timestamp.desc()).paginate(page=page, per_page=10)

    return flask.render_template(
        "drafts.html",
        pagination=pagination,
        drafts=pagination.items,
        operate_form=operate_form
    )


@posts_bp.route('/post/<post_slug>', methods=['GET'])
def post(post_slug):
    operate_form = OperateForm()
    post = Post.query.filter_by(slug=post_slug, is_draft=False).first_or_404()

    if not current_user.is_admin and post.is_privacy:
        flask.abort(403)

    post_visited.send(flask.current_app._get_current_object(), post=post)

    return flask.render_template(
        'post.html',
        post=post,
        operate_form=operate_form
    )


@posts_bp.route('/search', methods=['GET'])
def search_post():
    q = flask.request.args.get('q')
    page = int(flask.request.args.get('page', 1))
    # pagination = Post.query.filter(or_(Post.title.like(u'%{}%'.format(q)),
    #                                Post.body.like(u'%{}%'.format(q)))).paginate(page=page, per_page=10)
    pagination = Post.query.whooshee_search(q).order_by(Post.timestamp.desc()).paginate(page=page, per_page=10)
    return flask.render_template(
        "posts.html",
        pagination=pagination,
        posts=pagination.items
    )


@posts_bp.route('/post/create/<editor>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMINISTER')
def create_post(editor):
    post_form = PostForm()
    create_category_form = CreateForm()
    create_collection_form = CreateForm()
    create_tag_form = CreateForm()
    if post_form.validate_on_submit():
        title = post_form.title.data
        category = post_form.category.data
        collection = post_form.collection.data
        background = post_form.background_image_url.data
        tag_names = post_form.tags.data
        deny_comment = post_form.deny_comment.data
        privacy = post_form.privacy.data

        if editor == "markdown":
            content = post_form.body.data
            body = md.convert(content)
            is_markdown = True
        else:
            body = post_form.body.data
            is_markdown = False

        post = Post(
            title=title,
            slug=slugify(title, max_length=100),
            category=Category.query.filter_by(name=category).first(),
            collection=Collection.query.filter_by(name=collection).first(),
            tags=[Tag.query.filter_by(name=item).first() for item in tag_names],
            deny_comment=deny_comment,
            is_privacy=privacy,
            is_markdown=is_markdown,
            background=background,
            body=body,
            timestamp=datetime.now(),
            author=current_user
        )

        if editor == "markdown":
            post.content = content

        db.session.add(post)
        db.session.commit()

        if post_form.save_submit.data:
            post.is_draft = True
            db.session.commit()
            flask.flash(_("The Post has been saved as a Draft Successful!"), category="success")

        elif post_form.publish_submit.data:
            db.session.commit()
            flask.flash(_("Create A New Post Successful!"), category="success")

        return flask.redirect(flask.url_for('posts.posts'))

    return flask.render_template(
        'create.html',
        editor=editor,
        form=post_form,
        create_category_form=create_category_form,
        create_collection_form=create_collection_form,
        create_tag_form=create_tag_form
    )


@posts_bp.route('/post/edit/<post_slug>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMINISTER')
def edit_post(post_slug):
    post_form = PostForm()
    create_category_form = CreateForm()
    create_collection_form = CreateForm()
    create_tag_form = CreateForm()

    search_post = Post.query.filter_by(slug=post_slug).first_or_404()

    is_markdown = search_post.is_markdown

    post_form.title.data = search_post.title

    if search_post.category:
        post_form.category.data = search_post.category.name
    else:
        if Category.query.first():
            post_form.category.data = Category.query.first().name

    if search_post.collection:
        post_form.collection.data = search_post.collection.name
    else:
        post_form.collection.data = ""

    if search_post.tags:
        post_form.tags.data = [item.name for item in search_post.tags]
    else:
        if Tag.query.first():
            post_form.tags.data = [Tag.query.first().name]

    post_form.background_image_url.data = search_post.background
    post_form.deny_comment.data = search_post.deny_comment
    post_form.privacy.data = search_post.is_privacy

    if is_markdown:
        post_form.body.data = search_post.content
    else:
        post_form.body.data = search_post.body

    if post_form.validate_on_submit():
        title = flask.request.form.get('title')
        category_name = flask.request.form.get('category')

        collection_name = flask.request.form.get('collection')
        tag_names = flask.request.form.getlist('tags')
        background = flask.request.form.get('background_image_url')
        privacy = True if flask.request.form.get('privacy') else False

        if is_markdown:
            content = flask.request.form.get('body')
            body = md.convert(content)
        else:
            body = flask.request.form.get('body')

        search_post.title = title
        search_post.slug = slugify(title, max_length=100)

        category = Category.query.filter_by(name=category_name).first()
        if category:
            search_post.category = category

        collection = Collection.query.filter_by(name=collection_name).first()
        if collection:
            search_post.collection = collection

        search_post.tags = [Tag.query.filter_by(name=item).first() for item in tag_names]
        search_post.background = background
        search_post.is_privacy = privacy
        search_post.body = body
        search_post.timestamp=datetime.now()

        if is_markdown:
            search_post.content = content

        if post_form.save_submit.data:
            search_post.is_draft = True
            db.session.commit()
            flask.flash(_("The Post has been saved as a Draft Successful!"), category="success")
        elif post_form.publish_submit.data:
            search_post.is_draft = False
            db.session.commit()
            flask.flash(_("Update and Publish The Post Successful!"), category="success")

        return flask.redirect(flask.url_for('posts.posts'))

    return flask.render_template(
        'edit.html',
        form=post_form,
        post=search_post,
        create_category_form=create_category_form,
        create_collection_form=create_collection_form,
        create_tag_form=create_tag_form
    )


@posts_bp.route('/post/delete/<post_slug>', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def delete_post(post_slug):
    if flask.request.method == "POST":
        search_post = Post.query.filter_by(slug=post_slug).first_or_404()
        db.session.delete(search_post)
        flask.flash(_("Delete The Post Successful!"), category="success")
        return flask.redirect(flask.url_for('posts.posts'))


@posts_bp.route('/post/category/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_category():
    if flask.request.method == "POST":
        category_name = flask.request.form.get('name')
        if Category.query.filter_by(name=category_name).first():
            flask.flash(_("This Category already exists!"), category="warning")
            return redirect_back()

        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()
        return redirect_back()


@posts_bp.route('/post/collection/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_collection():
    if flask.request.method == "POST":
        collection_name = flask.request.form.get('name')
        if Collection.query.filter_by(name=collection_name).first():
            flask.flash(_("This Collection already exists!"), category="warning")
            return redirect_back()

        collection = Collection(name=collection_name)
        db.session.add(collection)
        db.session.commit()
        return redirect_back()


@posts_bp.route('/post/tag/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_tag():
    if flask.request.method == "POST":
        tag_name = flask.request.form.get('name')
        if Tag.query.filter_by(name=tag_name).first():
            flask.flash(_("This Tag already exists!"), category="warning")
            return redirect_back()

        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()
        return redirect_back()


@posts_bp.route('/post/create_comment/<post_slug>', methods=['POST'])
def create_comment(post_slug):
    if flask.request.method == "POST":
        search_post = Post.query.filter_by(slug=post_slug).first_or_404()
        author = flask.request.form.get("author")
        email = flask.request.form.get("email")
        body = flask.request.form.get("body")

        comment = Comment(
            author=author,
            email=email,
            body=body,
            post=search_post
        )

        db.session.add(comment)
        db.session.commit()
        return flask.redirect(flask.url_for('posts.post', post_slug=search_post.slug))


@posts_bp.route('/post/delete-comment/<comment_id>', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def delete_comment(comment_id):
    if flask.request.method == "POST":
        search_comment = Comment.query.get(comment_id)
        post_slug = search_comment.post.slug
        db.session.delete(search_comment)
        flask.flash(_("Delete The Comment Successful!"), category="success")
        return flask.redirect(flask.url_for('posts.post', post_slug=post_slug))

