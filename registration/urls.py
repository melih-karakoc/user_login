from django.urls import path, re_path, include
from . import views 
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from registration import views
from registration.forms import LoginForm

urlpatterns = [
    # path("register", views.register_attempt, name="register_attempt"),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('login/', views.CustomLoginView.as_view(
        redirect_authenticated_user=True, 
        template_name='registration/login.html',
        authentication_form=LoginForm), name='login'),
    path('register/', views.RegisterView.as_view(), name='registration-register'),
    path('profile/', views.profile, name='registration-profile'),
    path('verify-email-confirm/<uidb64>/<token>/', views.verify_email_confirm, name='verify-email-confirm'),
    # social auth
    path('initiate-auth/', views.initiate_social_auth, name='initiate_social_auth'),
    path('social-auth-callback/', views.social_auth_callback, name='social_auth_callback'),
]
