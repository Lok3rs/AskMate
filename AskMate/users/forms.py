from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from AskMate.users.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Matename",
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(f'Username {username.data} is taken.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(f'That email already exists in database.')


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=30)])
    remember = BooleanField("Remember Me")
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField("Matename",
                           validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    picture = FileField("Update profile picture",
                        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg', 'bmp'])])
    submit = SubmitField('Update')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(f'Username {username.data} is taken.')

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError(f'That email already exists in database.')


class RequestResetForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Request Reset Password")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(f'There is no account with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")
