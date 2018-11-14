from flask_mail import Message
from flask import render_template
from app import mail
from app import app
from threading import Thread


def send_async_email(app, msg):
    '''
    Sends email

    Args:
        app: flask app environment
        msg (str): message to send
    '''

    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    '''
    Starts a thread to send an email

    Args:
        subject (str): subject of the email
        sender (str): email address of sender
        recipients (list): list of recipient email addresses
        text_body (str): content of the email
        html_body (str): content of the email (in HTML)
    '''

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    '''
    Sends an email to reset a user's password

    Args:
        user (str): email of the user
    '''

    token = user.get_reset_password_token()
    send_email(
        '[UML ECRL] Reset Your Password',
        sender=app.config['MAIL_USERNAME'],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user,
            token=token
        ),
        html_body=render_template(
            'email/reset_password.html',
            user=user,
            token=token)
        )


def send_results(email, results, rmse, mae):
    '''
    Sends an email with prediction results

    Args:
        email (str): email of the recipient
        results (list): prediction results
        rmse (float): RMSE of the test set used to train the model
        mae (float): median absolute error of the test set used to train the
                     model
    '''

    with app.app_context():
        send_email(
            '[UML ECRL] Prediction Results',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            text_body=render_template(
                'email/results.txt',
                email=email,
                results=results,
                rmse=rmse,
                mae=mae
            ),
            html_body=render_template(
                'email/results.html',
                email=email,
                results=results,
                rmse=rmse,
                mae=mae
            )
        )
