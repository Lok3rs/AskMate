from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from AskMate.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from AskMate.answers.routes import answers
    from AskMate.users.routes import users
    from AskMate.comments.routes import comments
    from AskMate.main.routes import main
    from AskMate.questions.routes import questions
    from AskMate.tags.routes import tags
    from AskMate.errors.handlers import errors

    app.register_blueprint(answers)
    app.register_blueprint(users)
    app.register_blueprint(comments)
    app.register_blueprint(main)
    app.register_blueprint(questions)
    app.register_blueprint(tags)
    app.register_blueprint(errors)

    return app
