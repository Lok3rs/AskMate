import os

from flask import Blueprint, request, render_template, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, func

from AskMate import db
from AskMate.questions.models import Question
from AskMate.answers.models import Answer
from AskMate.questions.forms import QuestionForm
from AskMate.questions.utils import get_question
from AskMate.main.utils import save_picture

questions = Blueprint('questions', __name__)


@questions.route("/list", methods=["GET"])
def list_questions():
    order_dict = {
        "new_old": Question.submission_time.desc(), "old_new": Question.submission_time,
        "best_rate": Question.vote_number.desc(), "worst_rate": Question.vote_number,
        "most_views": Question.view_number.desc(), "least_views": Question.view_number
    }
    page = int(request.args.get('page', default=1))
    search_phrase = request.args.get("search_phrase") if request.args.get("search_phrase") else ""
    order_option = request.args.get("order_option") if request.args.get("order_option") else "new_old"
    questions = (Question.query.filter(or_(func.lower(Question.title).like(func.lower(f"%{search_phrase}%")),
                                           func.lower(Question.message).like(func.lower(f"%{search_phrase}%"))))
                 .order_by(order_dict[order_option]).paginate(per_page=50, page=page)) if search_phrase != "" \
        else Question.query.order_by(order_dict[order_option]).paginate(per_page=5, page=page)
    answers = Answer.query.filter(func.lower(Answer.message).like(func.lower(f"%{search_phrase}%")))
    return render_template("questions/list.html", questions=questions, search_phrase=search_phrase, answers=answers,
                           get_question=get_question)


@questions.route("/question/<question_id>", methods=["GET"])
def show_question(question_id):
    found_question = Question.query.get_or_404(question_id)
    found_question.view_number += 1
    db.session.commit()
    answers = Answer.query.filter(Answer.question_id == question_id).all()
    return render_template("questions/show_question.html", question=found_question,
                           answers=answers) if found_question else redirect(url_for("questions.list_questions"))


@questions.route("/ask", methods=["GET", "POST"])
@login_required
def ask_question():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(title=form.title.data, message=form.question.data, author=current_user)
        if form.picture.data:
            question.image = save_picture(form.picture.data, "upload", (1280, 720))
        db.session.add(question)
        db.session.commit()
        flash("Question asked!", "success")
        return redirect(url_for("questions.list_questions"))
    return render_template("questions/ask_question.html", form=form, title="Ask Question", legend='Ask a Question!', edit=False)


@questions.route("/question/edit/<question_id>", methods=["GET", "POST"])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if question.author != current_user:
        abort(403)
    form = QuestionForm()
    if form.validate_on_submit():
        question.title = form.title.data
        question.message = form.question.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'upload', (1024, 720))
            question.image = picture_file
        db.session.commit()
        flash("Question edited", "success")
        return redirect(url_for("questions.show_question", question_id=question_id))
    elif request.method == "GET":
        form.title.data = question.title
        form.question.data = question.message
    return render_template("questions/ask_question.html", form=form, title="Edit Question", legend='Edit Your Question',
                           question=question, edit=True)


@questions.route("/question/edit/<question_id>/delete_image", methods=["GET"])
@login_required
def delete_question_image(question_id):
    question = Question.query.get_or_404(question_id)
    if question.author != current_user:
        abort(403)
    picture_filepath = os.path.join(current_app.root_path, 'static/upload', question.image)
    if os.path.exists(picture_filepath):
        os.remove(picture_filepath)
    question.image = None
    db.session.commit()
    flash("Image deleted", "success")
    return redirect(url_for("questions.edit_question", question_id=question_id))


@questions.route("/question/<question_id>/<vote_option>", methods=["GET"])
def vote_on_question(question_id, vote_option):
    found_question = Question.query.get_or_404(question_id)
    if current_user.is_authenticated:
        if current_user.id == found_question.author.id:
            flash("You can't vote your own questions, bro", "danger")
        elif not found_question.voted_by or f"u{current_user.id}x" not in found_question.voted_by:
            if vote_option not in ["up", "down"]:
                abort(404)
            found_question.vote_number += 1 if vote_option == "up" else -1
            found_question.view_number -= 1
            found_question.voted_by = f"{found_question.voted_by}, u{current_user.id}x"
            db.session.commit()
            flash("Thanks for your vote!", "success")
        else:
            flash("You can vote only once on each question.", "danger")
    else:
        flash("Sign in to vote on questions.", "danger")
    return redirect(url_for("questions.show_question", question_id=question_id))


@questions.route("/question/<question_id>/delete", methods=["GET"])
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter(Answer.question_id == question_id).all()
    if current_user.id == question.author.id:
        if question.image:
            picture_filepath = os.path.join(current_app.root_path, 'static/upload', question.image)
            if os.path.exists(picture_filepath):
                os.remove(picture_filepath)
        for answer in answers:
            if answer.image:
                picture_filepath = os.path.join(current_app.root_path, 'static/upload', question.image)
                if os.path.exists(picture_filepath):
                    os.remove(picture_filepath)
        Answer.query.filter(Answer.question_id == question_id).delete()
        Question.query.filter(Question.id == question_id).delete()
        db.session.commit()
        flash("Question deleted successfully", "success")
    else:
        flash("You can't delete somebody's question", "danger")
        return redirect(url_for("questions.show_question", question_id=question_id))
    return redirect(url_for("questions.list_questions"))