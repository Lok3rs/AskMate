from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired


class AnswerForm(FlaskForm):
    answer = TextAreaField("Answer",
                           validators=[DataRequired()])
    picture = FileField("Upload picture for your answer (optional)",
                        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg', 'bmp'])])
    submit = SubmitField("Post an Answer")
    submit_edit = SubmitField("Accept Edition")