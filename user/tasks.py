from celery import shared_task
from config.celery import app
from .models import User
from django.core.mail import EmailMessage
import re
from django.core.mail import send_mail
from config import settings
import requests





def sanitize_email(email):
    # Убираем новые строки и пробелы в начале и конце
    return re.sub(r'[\r\n]+', '', email.strip())



@shared_task
def send_verificaation_code(application_id):

    try:
        application = User.objects.get(pk=application_id)
    except User.DoesNotExist:
        return
    
    email = application.email
    verification_code = application.verification_code

    subject = 'Подтвердите вашу почту'
    message = f'Уважаемый клиент, пожалуйста поддтвердите свою почту. Ваш код поддтверждения: {verification_code}'
    from_email = sanitize_email('flagman-inc@yandex.ru')
    recipient_list = [sanitize_email(email)]

    email_message = EmailMessage(subject, message, from_email, recipient_list)

    email_message.send(fail_silently=False)


@shared_task
def send_password_reset_code(user_id):
    user = User.objects.get(id=user_id)
    subject = 'Восстановление пароля'
    message = f'Ваш код восстановления: {user.password_reset_code}'
    from_email = sanitize_email('flagman-inc@yandex.ru')
    send_mail(subject, message, sanitize_email(from_email), [sanitize_email(user.email)])


@shared_task
def send_verificaation_code_to_new_email(user_id):
    user = User.objects.get(id=user_id)
    from_email = 'flagman-inc@yandex.ru'
    if user.new_email:
        send_mail(
            'Подтверждение нового email',
            f'Ваш код подтверждения: {user.new_email_verification_code}',
            sanitize_email(from_email),
            [user.new_email],
        )
