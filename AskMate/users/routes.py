from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required

from AskMate import bcrypt, db
from AskMate.users.models import User
from AskMate.questions.models import Question
from AskMate.answers.models import Answer
from AskMate.questions.utils import get_question
from AskMate.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from AskMate.users.utils import send_reset_email
from AskMate.main.utils import save_picture

users = Blueprint('users', __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Welcome, {form.username.data}! Feel free to ask about ANYTHING!", 'success')
        return redirect(url_for("users.login"))
    return render_template('users/register.html', form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("questions.list_questions"))
        else:
            flash("Login failed. Please check email and password", "danger")
    return render_template('users/login.html', form=form)


@users.route("/logout")
def logout():
    if not current_user.is_authenticated:
        flash("You can not logout if you're not logged in, mate!", "info")
        return redirect(url_for("login"))
    else:
        logout_user()
        flash("Logged out. See you again!", "success")
    return redirect(url_for("main.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'profile_pics', (125, 125))
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("users/account.html", form=form)


@users.route("/user/<username>")
def user_info(username):
    user = User.query.filter_by(username=username).first_or_404()
    questions = Question.query.filter_by(author=user).order_by(Question.submission_time.desc()).all()
    answers = Answer.query.filter_by(author=user).order_by(Answer.submission_time.desc()).all()
    return render_template("users/user_info.html", questions=questions, user=user,
                           answers=answers, get_question=get_question)


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Request sent. Check your email for further steps.", "info")
        return redirect(url_for("users.login"))
    return render_template("users/reset_request.html", form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_token(token)
    if not user:
        flash("Token is invalid or expired, request reset again", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash(f"Your password has been reset. You can login with that now.", 'success')
        return redirect(url_for("users.login"))
    return render_template("users/reset_token.html", form=form)