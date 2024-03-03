from django.contrib.auth import views as auth_views
from django.urls import path

from registration.forms import LoginForm

from . import views

urlpatterns = [
    # path("register", views.register_attempt, name="register_attempt"),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='registration/logout.html'),
        name='logout',
    ),
    path(
        'login/',
        views.CustomLoginView.as_view(
            redirect_authenticated_user=True,
            template_name='registration/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path('register/', views.RegisterView.as_view(), name='registration-register'),
    path('profile/', views.profile, name='registration-profile'),
    path(
        'verify-email-confirm/<uidb64>/<token>/',
        views.verify_email_confirm,
        name='verify-email-confirm',
    ),
    # social auth
    path(
        'initiate-auth/',
        views.InitiateSocialAuth.as_view(),
        name='initiate_social_auth',
    ),
    path(
        'social-auth-callback/',
        views.SocialAuthCallback.as_view(),
        name='social_auth_callback',
    ),
]
