import os
import secrets
from flask import render_template, flash, url_for, redirect, request
from inventory.forms import RegistrationForm, LoginForm, UpdateAccountForm
from inventory.models import User, Post
from inventory import app, bcrypt, db
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        "author": "Franky",
        "title": "Sample title",
        "date_posted": "March 27, 2019",
        "content": "sample content for sample post",
    },
    {
        "author": "James",
        "title": "Sample james",
        "date_posted": "March 27, 2019",
        "content": "sample content for james post",
    }
]

@app.route("/")
def home():
    return render_template("inventory/inventory_list.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('inventory/register.html', title="registration", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template('inventory/login.html', title="login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile picture', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/account', methods=["GET", "POST"])
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
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile picture/' + current_user.image_file)
    return render_template('inventory/account.html', title="account", image_file=image_file, form=form)