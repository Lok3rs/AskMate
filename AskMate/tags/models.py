from AskMate import db


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"Tag({self.name})"


class Question_Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)

    def __repr__(self):
        return f"Question_Tag(qid:{self.question_id}, tid:{self.tag_id})"