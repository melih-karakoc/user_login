from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIRequestFactory

from registration import helpers, views
from registration.models import User


class VerifyEmailConfirmTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret'
        )
        account_activation_token = helpers.TokenGenerator()
        self.token = account_activation_token.make_token(self.user)
        self.uuid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_verfiy_email_confirm(self):
        request = self.factory.get('verify-email-confirm/<uidb64>/<token>/')
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        request.user = self.user
        response = views.verify_email_confirm(request, self.uuid, self.token)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.profile.is_email_verified)
        self.assertEqual(response.url, '/registration/login/')


class RegisterViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'test@gmail.com',
            'first_name': 'test',
            'last_name': 'test',
        }

    def test_register_new_user(self):
        request = self.factory.post('/registration/register/', self.data)
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        response = views.RegisterView.as_view()(request)
        post_user = User.objects.get(email='test@gmail.com')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(post_user.email, 'test@gmail.com')


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.unverified_user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret'
        )

        self.verified_user = User.objects.create_user(
            username='jacob2', email='jacob2@…', password='top_secret'
        )
        profile = self.verified_user.profile
        profile.is_email_verified = True
        profile.save()
        self.login_data = {'username': 'jacob', 'password': 'top_secret'}
        self.verified_login_data = {'username': 'jacob2', 'password': 'top_secret'}

    def test_login(self):
        request = self.factory.post('/registration/login/', self.login_data)
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        views.CustomLoginView.as_view()(request)
        self.assertEqual(self.unverified_user.last_login, None)

        request = self.factory.post('/registration/login/', self.verified_login_data)
        request.user = AnonymousUser()
        request.session = self.client.session
        setattr(request, '_messages', FallbackStorage(request))

        views.CustomLoginView.as_view()(request)

        self.verified_user.refresh_from_db()
        self.assertIsNotNone(self.verified_user.last_login, None)
