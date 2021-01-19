from flask import url_for
from flask_mail import Message

from AskMate import mail


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Ask Mate - Reset Your Password",
                  sender="noreply@askmate.com",
                  recipients=[user.email])
    msg.body = f"""Hi Mate! Looks like you forgot your password. 
    To reset it visit following link {url_for("reset_token", token=token, _external=True)}

    If you did not request password reset, just ignore this email.

    Please don't answer at this mail.

    Best regards, Mate!
    Cheers!    
    """
    mail.send(msg)
