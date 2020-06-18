from datetime import datetime
import flask
from flask_security import login_required, current_user
from sqlalchemy import or_
from app.model.models import User, Post, Category, Tag, Archive, Relate, Comment
from app.form.forms import PostForm, OperateForm, CreateForm
from app.controller.extensions import db
from app.utils.common import redirect_back
from app.utils.decorator import permission_required

posts_bp = flask.Blueprint('posts', __name__, url_prefix='/')


@posts_bp.route('/', methods=['GET'])
def posts():
    today = datetime.today()
    weekday = today.isoweekday()
    author = User.query.get(1)

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

    pagination = posts.order_by(Post.publish_time.desc()).paginate(page=page, per_page=6)

    categories = Category.query.all()
    archives = Archive.query.all()
    tags = Tag.query.all()

    if pagination.page == 1:
        posts_template = "index.html"
    else:
        posts_template = "posts.html"

    latest_posts = Post.query.filter_by(is_draft=False).order_by(Post.publish_time.desc()).limit(3).all()
    older_posts = Post.query.filter_by(is_draft=False).order_by(Post.publish_time).limit(3).all()

    return flask.render_template(
        posts_template,
        author=author,
        pagination=pagination,
        posts=pagination.items,
        post=None,
        categories=categories,
        tags=tags,
        archives=archives,
        latest_posts=latest_posts,
        older_posts=older_posts,
        weekday=weekday
    )


@posts_bp.route('/post/<post_slug>', methods=['GET'])
def post(post_slug):
    operate_form = OperateForm()
    author = User.query.get(1)

    post = Post.query.filter_by(slug=post_slug).first_or_404()

    categories = Category.query.all()
    archives = Archive.query.all()
    tags = Tag.query.all()

    latest_posts = Post.query.filter_by(is_draft=False).order_by(Post.publish_time.desc()).limit(3).all()
    older_posts = Post.query.filter_by(is_draft=False).order_by(Post.publish_time).limit(3).all()

    return flask.render_template(
        'post.html',
        author=author,
        post=post,
        categories=categories,
        tags=tags,
        archives=archives,
        latest_posts=latest_posts,
        older_posts=older_posts,
        operate_form=operate_form
    )


@posts_bp.route('/search', methods=['GET'])
def search_post():
    author = User.query.get(1)

    q = flask.request.args.get('q')
    page = int(flask.request.args.get('page', 1))
    result = Post.query.filter(or_(Post.title.like(u'%{}%'.format(q)),
                                   Post.abstract.like(u'%{}%'.format(q)),
                                   Post.body.like(u'%{}%'.format(q))))
    pagination = result.paginate(page=page, per_page=6)
    return flask.render_template(
        "posts.html",
        author=author,
        pagination=pagination,
        posts=pagination.items
    )


@posts_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
@permission_required('ADMINISTER')
def create_post():
    post_form = PostForm()
    create_category_form = CreateForm()
    create_relate_form = CreateForm()
    create_tag_form = CreateForm()
    if post_form.validate_on_submit():
        title = post_form.title.data
        category = post_form.category.data
        relate = post_form.relate.data
        tag_names = post_form.tags.data
        slug = post_form.slug.data
        abstract = post_form.abstract.data
        deny_comment = post_form.deny_comment.data
        body = post_form.body.data

        if Post.query.filter_by(slug=slug).first():
            flask.flash("This Slug is already in use!", category="warning")
            return flask.redirect(flask.url_for('posts.create_post'))

        post = Post(
            title=title,
            category=Category.query.filter_by(name=category).first(),
            relate=Relate.query.filter_by(name=relate).first(),
            tags=[Tag.query.filter_by(name=item).first() for item in tag_names],
            slug=slug,
            abstract=abstract,
            deny_comment=deny_comment,
            body=body,
            author=current_user
        )

        db.session.add(post)
        db.session.commit()

        if post_form.save_submit.data:
            post.is_draft = True
        elif post_form.publish_submit.data:
            post.publish_time = datetime.now()
        db.session.commit()
        flask.flash("Create A Post Successful!", category="success")
        return flask.redirect(flask.url_for('posts.post', post_slug=slug))
    return flask.render_template(
        'create.html',
        form=post_form,
        post=None,
        create_category_form=create_category_form,
        create_relate_form=create_relate_form,
        create_tag_form=create_tag_form
    )


@posts_bp.route('/post/edit/<post_slug>', methods=['GET', 'POST'])
@login_required
@permission_required('ADMINISTER')
def edit_post(post_slug):
    post_form = PostForm()
    create_category_form = CreateForm()
    create_relate_form = CreateForm()
    create_tag_form = CreateForm()

    search_post = Post.query.filter_by(slug=post_slug).first_or_404()

    post_form.title.data = search_post.title

    if search_post.category:
        post_form.category.data = search_post.category.name
    else:
        if Category.query.first():
            post_form.category.data = Category.query.first().name

    if search_post.relate:
        post_form.relate.data = search_post.relate.name
    else:
        post_form.relate.data = ""

    if search_post.tags:
        post_form.tags.data = [item.name for item in search_post.tags]
    else:
        if Tag.query.first():
            post_form.tags.data = [Tag.query.first().name]

    post_form.slug.data = search_post.slug
    post_form.abstract.data = search_post.abstract
    post_form.deny_comment.data = search_post.deny_comment
    post_form.body.data = search_post.body

    if post_form.validate_on_submit():
        title = flask.request.form.get('title')
        category_name = flask.request.form.get('category')

        relate_name = flask.request.form.get('relate')
        tag_names = flask.request.form.getlist('tags')
        slug = flask.request.form.get('slug')
        abstract = flask.request.form.get('abstract')
        deny_comment = True if flask.request.form.get('deny_comment') else False
        body = flask.request.form.get('body')

        if slug != search_post.slug and Post.query.filter_by(slug=slug).first():
            flask.flash("This Slug is already in use!", category="warning")
            return flask.redirect(flask.url_for('posts.edit_post', post_slug=search_post.slug))

        search_post.title = title

        category = Category.query.filter_by(name=category_name).first()
        if category:
            search_post.category = category

        relate = Relate.query.filter_by(name=relate_name).first()
        if relate:
            search_post.relate = relate

        search_post.tags = [Tag.query.filter_by(name=item).first() for item in tag_names]
        search_post.slug = slug
        search_post.abstract = abstract
        search_post.deny_comment = deny_comment
        search_post.body = body

        if post_form.save_submit.data:
            search_post.is_draft = True
        elif post_form.publish_submit.data:
            search_post.publish_time = datetime.now()

        db.session.commit()
        flask.flash("Edit The Post Successful!", category="success")
        return flask.redirect(flask.url_for('posts.post', post_slug=search_post.slug))

    return flask.render_template(
        'create.html',
        form=post_form,
        post=search_post,
        create_category_form=create_category_form,
        create_relate_form=create_relate_form,
        create_tag_form=create_tag_form
    )


@posts_bp.route('/post/delete/<post_slug>', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def delete_post(post_slug):
    if flask.request.method == "POST":
        search_post = Post.query.filter_by(slug=post_slug).first_or_404()
        db.session.delete(search_post)
        flask.flash("Delete The Post Successful!", category="success")
        return flask.redirect(flask.url_for('posts.posts'))


@posts_bp.route('/post/category/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_category():
    if flask.request.method == "POST":
        category_name = flask.request.form.get('name')
        if Category.query.filter_by(name=category_name).first():
            flask.flash("This Category is already existed!", category="warning")
            return redirect_back()

        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()
        return redirect_back()


@posts_bp.route('/post/relate/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_relate():
    if flask.request.method == "POST":
        relate_name = flask.request.form.get('name')
        if Relate.query.filter_by(name=relate_name).first():
            flask.flash("This Relate is already existed!", category="warning")
            return redirect_back()

        relate = Relate(name=relate_name)
        db.session.add(relate)
        db.session.commit()
        return redirect_back()


@posts_bp.route('/post/tag/new', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def create_tag():
    if flask.request.method == "POST":
        tag_name = flask.request.form.get('name')
        if Tag.query.filter_by(name=tag_name).first():
            flask.flash("This Tag is already existed!", category="warning")
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
        # flask.flash('Thanks, your comment will be published after reviewed.', 'info')
        return redirect_back()


@posts_bp.route('/post/delete-comment/<comment_id>', methods=['POST'])
@login_required
@permission_required('ADMINISTER')
def delete_comment(comment_id):
    if flask.request.method == "POST":
        search_comment = Comment.query.get(comment_id)
        db.session.delete(search_comment)
        flask.flash("Delete The Comment Successful!", category="success")
        return redirect_back()
