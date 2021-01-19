from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    title = StringField("Title",
                        validators=[DataRequired()])
    question = TextAreaField("Question",
                             validators=[DataRequired()])
    picture = FileField("Upload picture for your question (optional)",
                        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg', 'bmp'])])
    submit = SubmitField("Ask Question")
    submit_edit = SubmitField("Accept Edition")
