from datetime import datetime
import flask
from flask_security import login_required, current_user
from sqlalchemy import func
from slugify import slugify
from flask_babelex import gettext as _
from app.model.models import Post, Category, Tag, Archive, Collection, Comment, About
from app.form.forms import PostForm, OperateForm, CreateForm, CreateTopicForm
from app.controller.extensions import db
from app.utils.common import redirect_back
from app.utils.decorator import permission_required
from app.controller.signals import post_visited
from app.controller.md_ext import md

posts_bp = flask.Blueprint('posts', __name__, url_prefix='/')


@posts_bp.route('/', methods=['GET'])
def posts():
    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=False).\
        order_by(Post.is_top.desc()).\
        order_by(Post.timestamp.desc()).\
        paginate(page=page, per_page=10)
    count_post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).scalar()

    if pagination.page == 1:
        posts_template = "index.html"
    else:
        posts_template = "posts.html"

    return flask.render_template(
        posts_template,
        pagination=pagination,
        posts=pagination.items,
        count_post_nums=count_post_nums
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


@posts_bp.route('/tags', methods=['GET'])
def tags():
    tags = Tag.query.all()
    return flask.render_template("tags.html", tags=tags)


@posts_bp.route('/topics', methods=['GET'])
def topics():
    page = int(flask.request.args.get('page', 1))
    pagination = Collection.query.paginate(page=page, per_page=6)
    return flask.render_template(
        "topics.html",
        pagination=pagination,
        topics=pagination.items
    )


@posts_bp.route('/topic/<int:topic_id>', methods=['GET'])
def topic(topic_id):
    search_topic = Collection.query.get(topic_id)
    if not search_topic:
        flask.abort(404)

    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=False, collection_id=topic_id). \
        order_by(Post.is_top.desc()). \
        order_by(Post.timestamp.desc()). \
        paginate(page=page, per_page=10)

    count_post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False, collection_id=topic_id).scalar()

    return flask.render_template(
        "topic.html",
        pagination=pagination,
        posts=pagination.items,
        topic=search_topic,
        count_post_nums=count_post_nums
    )


@posts_bp.route('/tag/<int:tag_id>', methods=['GET'])
def tag(tag_id):
    search_tag = Tag.query.get(tag_id)
    if not search_tag:
        flask.abort(404)

    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=False).filter(Post.tags.contains(search_tag)). \
        order_by(Post.is_top.desc()). \
        order_by(Post.timestamp.desc()). \
        paginate(page=page, per_page=10)

    count_post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).\
        filter(Post.tags.contains(search_tag)).scalar()

    posts_template = "posts.html"

    return flask.render_template(
        posts_template,
        pagination=pagination,
        posts=pagination.items,
        tag=search_tag,
        count_post_nums=count_post_nums
    )


@posts_bp.route('/category/<int:category_id>', methods=['GET'])
def category(category_id):
    search_category = Category.query.get(category_id)
    if not search_category:
        flask.abort(404)

    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=False).filter_by(category=search_category). \
        order_by(Post.is_top.desc()). \
        order_by(Post.timestamp.desc()). \
        paginate(page=page, per_page=10)

    count_post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).\
        filter_by(category=search_category).scalar()

    posts_template = "posts.html"

    return flask.render_template(
        posts_template,
        pagination=pagination,
        posts=pagination.items,
        category=search_category,
        count_post_nums=count_post_nums
    )


@posts_bp.route('/archive/<int:archive_id>', methods=['GET'])
def archive(archive_id):
    search_archive = Archive.query.get(archive_id)
    if not search_archive:
        flask.abort(404)

    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=False).filter_by(archive_id=archive_id). \
        order_by(Post.is_top.desc()). \
        order_by(Post.timestamp.desc()). \
        paginate(page=page, per_page=10)
    count_post_nums = db.session.query(func.count(Post.id)).filter_by(is_draft=False).\
        filter_by(archive_id=archive_id).scalar()

    posts_template = "posts.html"

    return flask.render_template(
        posts_template,
        pagination=pagination,
        posts=pagination.items,
        archive=search_archive,
        count_post_nums=count_post_nums
    )


@posts_bp.route('/drafts', methods=['GET'])
@login_required
@permission_required('ADMINISTER')
def draft():
    operate_form = OperateForm()
    page = int(flask.request.args.get('page', 1))
    pagination = Post.query.filter_by(is_draft=True).paginate(page=page, per_page=10)

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
    pagination = Post.query.whooshee_search(q, order_by_relevance=0).paginate(page=page, per_page=10)
    count_post_nums = Post.query.whooshee_search(q, order_by_relevance=0).count()
    return flask.render_template(
        "posts.html",
        pagination=pagination,
        posts=pagination.items,
        count_post_nums=count_post_nums
    )


@posts_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
@permission_required('ADMINISTER')
def create_post():
    post_form = PostForm()
    create_category_form = CreateForm()
    create_collection_form = CreateTopicForm()
    create_tag_form = CreateForm()
    if post_form.validate_on_submit():
        title = post_form.title.data
        category = post_form.category.data
        collection = post_form.collection.data
        background = post_form.background_image_url.data
        tag_names = post_form.tags.data
        deny_comment = post_form.deny_comment.data
        privacy = post_form.privacy.data
        top = post_form.top.data
        is_markdown = post_form.is_markdown.data

        if is_markdown:
            content = post_form.body.data
            body = md.convert(content)
            markdown = True
        else:
            body = post_form.body.data
            markdown = False

        slug = slugify(title, max_length=100)
        if Post.query.filter_by(slug=slug).first():
            flask.flash(_("This post name already exists, choose an other name."), category="warning")
            return redirect_back()

        post = Post(
            title=title,
            slug=slug,
            category=Category.query.filter_by(name=category).first(),
            collection=Collection.query.filter_by(name=collection).first(),
            tags=[Tag.query.filter_by(name=item).first() for item in tag_names],
            deny_comment=deny_comment,
            is_privacy=privacy,
            is_top=top,
            is_markdown=markdown,
            background=background,
            body=body,
            timestamp=datetime.now(),
            author=current_user
        )

        if is_markdown:
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

        return flask.redirect(flask.url_for('posts.post', post_slug=slug))

    return flask.render_template(
        'create.html',
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
    create_collection_form = CreateTopicForm()
    create_tag_form = CreateForm()

    search_post = Post.query.filter_by(slug=post_slug).first_or_404()

    is_markdown = search_post.is_markdown

    post_form.title.data = search_post.title
    old_slug = search_post.slug

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
    post_form.top.data = search_post.is_top
    post_form.is_markdown.data = is_markdown

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
        top = True if flask.request.form.get('top') else False

        if is_markdown:
            content = flask.request.form.get('body')
            body = md.convert(content)
        else:
            body = flask.request.form.get('body')

        new_slug = slugify(title, max_length=100)

        if new_slug != old_slug and Post.query.filter_by(slug=new_slug).first():
            flask.flash(_("This post name already exists, choose an other name."), category="warning")
            return redirect_back()

        search_post.title = title
        search_post.slug = new_slug

        category = Category.query.filter_by(name=category_name).first()
        if category:
            search_post.category = category

        collection = Collection.query.filter_by(name=collection_name).first()
        if collection:
            search_post.collection = collection

        search_post.tags = [Tag.query.filter_by(name=item).first() for item in tag_names]
        search_post.background = background
        search_post.is_privacy = privacy
        search_post.is_top = top
        search_post.body = body
        # search_post.timestamp = datetime.now()

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

        return flask.redirect(flask.url_for('posts.post', post_slug=new_slug))

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
    search_post = Post.query.filter_by(slug=post_slug).first_or_404()
    db.session.delete(search_post)
    flask.flash(_("Delete The Post Successful!"), category="success")
    return flask.redirect(flask.url_for('posts.posts'))


@posts_bp.route('/post/category/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_category():
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
    collection_name = flask.request.form.get('name')
    collection_description = flask.request.form.get('description')
    collection_background = flask.request.form.get('background')
    if Collection.query.filter_by(name=collection_name).first():
        flask.flash(_("This topic already exists!"), category="warning")
        return redirect_back()

    collection = Collection(
        name=collection_name,
        description=collection_description,
        background=collection_background
    )
    db.session.add(collection)
    db.session.commit()
    return redirect_back()


@posts_bp.route('/post/tag/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_tag():
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
    search_post = Post.query.filter_by(slug=post_slug).first_or_404()
    author = flask.request.form.get("author")
    email = flask.request.form.get("email")
    body = flask.request.form.get("body")

    comment = Comment(
        author=author,
        email=email,
        body=body,
        post_id=search_post.id
    )

    db.session.add(comment)
    db.session.commit()
    return flask.redirect(flask.url_for('posts.post', post_slug=search_post.slug))


@posts_bp.route('/post/delete-comment/<comment_id>', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def delete_comment(comment_id):
    search_comment = Comment.query.get(comment_id)
    post_slug = search_comment.post.slug
    db.session.delete(search_comment)
    flask.flash(_("Delete The Comment Successful!"), category="success")
    return flask.redirect(flask.url_for('posts.post', post_slug=post_slug))


@posts_bp.route('/about')
def about():
    about = About.query.first()
    return flask.render_template("about.html", about=about)