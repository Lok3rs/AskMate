from datetime import datetime

from AskMate import db


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    vote_number = db.Column(db.Integer, nullable=False, default=0)
    view_number = db.Column(db.Integer, nullable=False, default=0)
    image = db.Column(db.String(60), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voted_by = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"Question('{self.title}', '{self.submission_time}')"