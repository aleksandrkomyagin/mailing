from time import sleep

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from mailing.celery import app
from mailing.settings import EMAIL_HOST_USER

from .models import Mailing

User = get_user_model()


@app.task(bind=True)
def send_email_task(self, mailing_id, recipient_list,
                    countdown=None, eta=None, expires=None):

    mailing = Mailing.objects.get(pk=mailing_id)
    for email in recipient_list:
        sleep(2)
        send_mail(
            subject='subject',
            message=f'{mailing.text}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
        )
    mailing.mail.update(status=True)


@app.task(bind=True)
def send_report_task(self):
    clients = User.objects.filter(role='moderator')
    email_list = [client.email for client in clients]
    for email in email_list:
        sleep(2)
        send_mail(
            subject='subject',
            message='отчет',
            from_email=EMAIL_HOST_USER,
            recipient_list=[email],
        )


@app.task(bind=True)
def send_password_task(self, user_email, password, confirmation_code):

    send_mail(
        subject='password',
        message=f'Ваш пароль:({password}) и'
                f' код подтверждения:({confirmation_code})',
        from_email=EMAIL_HOST_USER,
        recipient_list=[user_email],
    )
