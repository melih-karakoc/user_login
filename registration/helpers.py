from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from six import text_type

from registration import tasks
from registration.models import User


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk)
            + text_type(timestamp)
            + text_type(user.profile.is_email_verified)
        )


def create_form_user(form):
    with transaction.atomic():
        if form.is_valid():
            user = form.save()
            return user


def send_verification_email(request, user):
    domain = get_current_site(request).domain
    scheme = request.scheme

    tasks.send_verification_email.apply_async(args=[scheme, domain, user.id])


def update_profile(user):
    with transaction.atomic():
        profile = user.profile
        profile.is_email_verified = True
        profile.save()
        user.save()


def create_user(user_data):
    with transaction.atomic():
        user = User.objects.get_or_create(
            email=user_data['email'], defaults={'first_name': user_data['name']}
        )
        return user
