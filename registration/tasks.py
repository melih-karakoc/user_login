from celery import shared_task

from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .helpers import TokenGenerator


@shared_task
def send_verification_email(scheme, domain, user_id):
    print("SCHEME" + scheme)

    user = User.objects.get(pk=user_id)
    profile = user.profile
    email = user.email
    subject = "Verify Email"
    account_activation_token = TokenGenerator()

    message = render_to_string('registration/verify_email_message.html', {
        'scheme': scheme,
        'user': user,
        'domain': domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
    })
    email = EmailMessage(
        subject, message, to=[email]
    )
    email.content_subtype = 'html'
    email.send() 
