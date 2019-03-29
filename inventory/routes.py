from flask import render_template, flash, url_for, redirect
from inventory.forms import RegistrationForm, LoginForm
from inventory.models import User, Post
from inventory import app, bcrypt, db
from flask_login import login_user, current_user, logout_user

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
            return redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template('inventory/login.html', title="login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/account')
def account():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('inventory/account.html', title="account")