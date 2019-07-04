# coding=utf-8
# python3


from flask import render_template, session, redirect, flash, abort, url_for, current_app, make_response, request
from flask_login import current_user, login_required
from app.main import main
from app.email import send_email
from app.main.forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm
from app import db
from app.models import User
from app.common.logger import create_logger
import arrow
import hashlib

logger = create_logger(__name__)


@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if form.validate_on_submit():
        db.session.execute("insert into posts (body,author_id) values ('{}',{})".format(form.body.data, current_user.id))
        db.session.commit()
        form.body.data = ""
        return redirect(url_for(".index"))

    limit = 20
    if current_user.is_authenticated and session["is_followings"] == 1:
        sql = """
        select p.id,p.body,p.create_time,u.username,u.email_hash 
        from posts p 
        join users u on p.author_id=u.id 
        where p.author_id in (select followed_id from follows where follower_id={id})
        order by p.create_time desc
        limit {limit}
        """.format(id=current_user.id, limit=limit)
    else:
        sql = """
        select p.id,p.body,p.create_time,u.username,u.email_hash 
        from posts p 
        join users u on p.author_id=u.id 
        order by p.create_time desc
        limit {limit}
        """.format(limit=limit)
    # posts = db.engine.execute(sql)
    # 使用pandas调用实现分页restful api，ajax调用
    posts = []
    for row in db.engine.execute(sql):
        tmp = {}
        for k in row.keys():
            tmp[k] = row[k]
        tmp["create_time_utc"] = arrow.get(row["create_time"], current_app.config["TIME_ZONE"]).to("utc")
        posts.append(tmp)
    return render_template("index.html",
                           current_time=arrow.utcnow().datetime,
                           form=form,
                           posts=posts)


@main.route("/show_all")
def show_all():
    resp = make_response(redirect(url_for(".index")))
    session["is_followings"] = 0
    # 不用设置session也可以通过设置cookie的方法
    # resp.set_cookie("is_followings", 0, max_age=30 * 24 * 60 * 60)  # 30天
    return resp


@main.route("/show_followings")
@login_required
def show_followings():
    resp = make_response(redirect(url_for(".index")))
    session["is_followings"] = 1
    # 不用设置session也可以通过设置cookie的方法
    # resp.set_cookie("is_followings", 1, max_age=30 * 24 * 60 * 60)  # 30天
    return resp


@main.route("/user/<username>")
@login_required
def user(username):
    one_user = User(username=username)
    if not one_user.password_hash:
        abort(404)
    sql = "select p.id,p.body,p.create_time,u.username,u.email_hash from posts p join users u on p.author_id=u.id where u.id={} order by p.create_time desc".format(one_user.id)
    posts = db.engine.execute(sql)
    return render_template("user_posts.html", user=one_user, posts=posts)


@main.route("/followers/<username>")
@login_required
def followers(username):
    one_user = User(username=username)
    if one_user.id == 0:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    sql = """
    select t.followed_id,
           s.username,
           case when s.gender='M' then '男' when s.gender='F' then '女' else '' end as gender,
           floor(datediff(now(),s.birthday)/365) as age,
           s.location,
           s.about_me,
           s.email_hash 
    from follows t 
    join users s on t.followed_id=s.id 
    where t.follower_id={}
    """.format(one_user.id)
    all_followers = db.engine.execute(sql)
    return render_template('user_followers.html', user=one_user, result=all_followers)


@main.route("/followeds/<username>")
@login_required
def followeds(username):
    one_user = User(username=username)
    if one_user.id == 0:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    sql = """
    select t.followed_id,
           s.username,
           case when s.gender='M' then '男' when s.gender='F' then '女' else '' end as gender,
           floor(datediff(now(),s.birthday)/365) as age,
           s.location,
           s.about_me,
           s.email_hash 
    from follows t 
    join users s on t.follower_id=s.id 
    where t.followed_id={}
    """.format(one_user.id)
    all_followeds = db.engine.execute(sql)
    return render_template('user_followeds.html', user=one_user, result=all_followeds)


@main.route("/follow/<username>")
@login_required
def follow(username):
    one_user = User(username=username)
    if one_user.id == 0:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if current_user.is_following(one_user.id):
        flash("You are already following this user.")
        return redirect(url_for(".user", username=username))
    current_user.follow(one_user.id)
    flash("You are now following {}".format(username))
    return redirect(url_for(".user", username=username))


@main.route("/unfollow/<username>")
@login_required
def unfollow(username):
    one_user = User(username=username)
    if one_user.id == 0:
        flash("Invalid user.")
        return redirect(url_for(".index"))
    if not current_user.is_following(one_user.id):
        flash("You are not following this user.")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(one_user.id)
    flash("You are not following {} anymore.".format(username))
    return redirect(url_for(".user", username=username))


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        db.session.execute("update users set real_name='{}', location='{}', about_me='{}' where username='{}'".format(form.real_name.data, form.location.data, form.about_me.data, current_user.username))
        db.session.commit()
        current_user.real_name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        flash("Your profile has been updated.")
        return redirect(url_for(".user", username=current_user.username))
    form.real_name.data = current_user.real_name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@main.route("/post/<int:id>", methods=["GET", "POST"])
@login_required
def post(id):
    form = CommentForm()
    if form.validate_on_submit():
        sql = "insert into comments (body,author_id,post_id) values ('{}',{},{})".format(form.body.data, current_user.id, id)
        db.session.execute(sql)
        db.session.commit()
        flash("Your comment has been published.")
        return redirect(url_for(".post", id=id))
    post_sql = """
    select p.id,p.body,p.create_time,u.username,u.email_hash 
    from posts p 
    join users u on p.author_id=u.id 
    where p.id={}
    """.format(id)
    one_post = db.engine.execute(post_sql)
    comments_sql = """
    select c.body,c.body_html,c.create_time,c.disabled,u.username,u.email_hash 
    from comments c 
    join users u on c.author_id=u.id 
    where c.post_id={} 
    order by c.create_time desc
    """.format(id)
    all_comments = db.engine.execute(comments_sql)
    return render_template("post.html", form=form, posts=one_post, comments=all_comments)


@main.route("/maze/<username>")
@login_required
def maze(username):
    return "{}'s maze".format(username)


@main.route("/faq")
@login_required
def faq():
    form = CommentForm()
    return render_template("FAQ.html", form=form)


@main.route("/avatars")
def profile_avatars():
    email_hash = hashlib.md5('le7yi_ss@163.com'.lower().encode('utf-8')).hexdigest()
    return render_template('avatars.html', email_hash=email_hash)
