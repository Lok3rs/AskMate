import os
from flask import Blueprint, flash, redirect, render_template, url_for, request, abort, current_app
from flask_login import login_required, current_user

from AskMate import db
from AskMate.answers.forms import AnswerForm
from AskMate.questions.models import Question
from AskMate.answers.models import Answer
from AskMate.main.utils import save_picture

answers = Blueprint('answers', __name__)


@answers.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
@login_required
def post_an_answer(question_id):
    form = \
        AnswerForm()
    if form.validate_on_submit():
        answer = Answer(message=form.answer.data, author=current_user, question_id=question_id)
        if form.picture.data:
            answer.image = save_picture(form.picture.data, "upload", (1280, 720))
        db.session.add(answer)
        db.session.commit()
        flash("Answer posted!", "success")
        return redirect(
            url_for("questions.show_question", question_id=question_id))
    return render_template("answers/post_an_answer.html", form=form, title="Answer", legend='Answer your mate!', edit=False)


@answers.route("/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if answer.author != current_user:
        abort(403)
    form = AnswerForm()
    if form.validate_on_submit():
        answer.message = form.answer.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 'upload', (1024, 720))
            answer.image = picture_file
        db.session.commit()
        flash("Answer edited", "success")
        return redirect(url_for("questions.show_question", question_id=answer.question_id))
    elif request.method == "GET":
        form.answer.data = answer.message
    return render_template("answers/post_an_answer.html", form=form, title="Edit Answer", legend='Edit Answer',
                           answer=answer, edit=True)


@answers.route("/answer/<answer_id>/delete", methods=["GET"])
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    qid = answer.question_id
    if current_user.id == answer.author.id:
        if answer.image:
            picture_filepath = os.path.join(current_app.root_path, 'static/upload', answer.image)
            if os.path.exists(picture_filepath):
                os.remove(picture_filepath)
        Answer.query.filter(Answer.id == answer_id).delete()
        db.session.commit()
        flash("Answer deleted", "success")
    else:
        flash("You can't delete somebody's answer", "danger")
        return redirect(url_for("questions.show_question", question_id=answer.question_id))
    return redirect(url_for("questions.show_question", question_id=qid))


@answers.route("/answer/<answer_id>/delete_image", methods=["GET"])
def delete_answer_image(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    if answer.author != current_user:
        abort(403)
    picture_filepath = os.path.join(current_app.root_path, 'static/upload', answer.image)
    if os.path.exists(picture_filepath):
        os.remove(picture_filepath)
    answer.image = None
    db.session.commit()
    flash("Image deleted", "success")
    return redirect(url_for("answers.edit_answer", answer_id=answer_id))


@answers.route("/answer/<answer_id>/<vote_option>/<question_id>")
def vote_on_answer(answer_id, vote_option, question_id):
    answer = Answer.query.get_or_404(answer_id)
    question = Question.query.get_or_404(question_id)
    if current_user.is_authenticated:
        if current_user.id == answer.author.id:
            flash("You can't vote your own answers, bro", "danger")
        elif not answer.voted_by or f"u{current_user.id}x" not in answer.voted_by:
            answer.vote_number += 1 if vote_option == "up" else -1
            question.view_number -= 1
            answer.voted_by = f"{answer.voted_by}, u{current_user.id}x"
            db.session.commit()
            flash("Thanks for your vote!", "success")
        else:
            flash("You can vote only once on each answer.", "danger")
    else:
        flash("Sign in to vote on answers.", "danger")
    return redirect(url_for("questions.show_question", question_id=question_id))

