from AskMate.questions.models import Question


def get_question(question_id):
    return Question.query.filter(Question.id == question_id).first()
