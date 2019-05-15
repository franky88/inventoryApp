import uuid
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from inventory import db, bcrypt
from inventory.models import User, Post
from inventory.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from inventory.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    # if not current_user.is_authenticated:
    #     flash('Access denied!', 'danger')
    #     return redirect(url_for('main.home'))
    # if not current_user.admin:
    #     flash('Access Denied!', 'danger')
    #     return redirect(url_for('main.home'))
    if current_user.is_authenticated:
        flash('Already registered!', 'info')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(public_id=str(uuid.uuid4()), username=form.username.data, email=form.email.data, password=hashed_password, admin=False, active=True)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/register.html', title="registration", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('Already login!', 'info')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user.active:
            flash('Oops! Your account is deactivated! please visit network admin for account activation!', 'info')
            return redirect(url_for('users.login'))
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.home'))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template('users/login.html', title="login", form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

@users.route('/users', methods=['GET'])
@login_required
def all_users():
    if not current_user.admin:
        flash('Access Denied!', 'danger')
        return redirect(url_for('main.home'))
    users = User.query.all()
    return render_template('users/user_list.html', title="users", users=users)

@users.route('/users/<public_id>', methods=['GET'])
@login_required
def get_user(public_id):
    if not current_user.admin:
        flash('Access Denied!', 'danger')
        return redirect(url_for('main.home'))
    user = User.query.filter_by(public_id=public_id).first()
    return render_template('users/get_user.html', title="user", user=user)

@users.route('/users/<public_id>/delete', methods=['POST'])
@login_required
def delete_user(public_id):
    user = User.query.get_or_404(public_id)
    if not current_user.admin:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('main.home'))

@users.route('/users/<public_id>/deactivate', methods=['POST'])
@login_required
def deactivate_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not current_user.admin:
        abort(403)
    user.active = False
    db.session.commit()
    flash('User has been deactivated!', 'success')
    return redirect(url_for('users.get_user', public_id=user.public_id))

@users.route('/users/<public_id>/activate', methods=['POST'])
@login_required
def activate_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not current_user.admin:
        abort(403)
    user.active = True
    db.session.commit()
    flash('User has been activated!', 'success')
    return redirect(url_for('users.get_user', public_id=user.public_id))

@users.route('/users/<public_id>/promote', methods=['POST'])
@login_required
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not current_user.admin:
        abort(403)
    user.admin = True
    db.session.commit()
    flash('User has been promoted!', 'success')
    return redirect(url_for('users.get_user', public_id=user.public_id))

@users.route('/users/<public_id>/demoted', methods=['POST'])
@login_required
def demote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not current_user.admin:
        abort(403)
    user.admin = False
    db.session.commit()
    flash('User has been demoted!', 'success')
    return redirect(url_for('users.get_user', public_id=user.public_id))

@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for('users.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile picture/' + current_user.image_file)
    return render_template('users/account.html', title="account", image_file=image_file, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.timestamp.desc())\
        .paginate(page=page, per_page=5)
    return render_template("users/user_posts.html", posts=posts, user=user)

@users.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form)

@users.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your passord has been updated! You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form)