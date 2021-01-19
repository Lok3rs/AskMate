from datetime import datetime

from AskMate import db


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    vote_number = db.Column(db.Integer, nullable=False, default=0)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    submission_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(60), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voted_by = db.Column(db.String(), nullable=True)

    def __repr__(self):
        return f"Answer({self.message}, {self.submission_time}. Question_id={self.question_id})"
