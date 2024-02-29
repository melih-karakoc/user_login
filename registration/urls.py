from django.urls import path, re_path, include
from . import views 
from rest_framework.routers import DefaultRouter
from registration.views import CustomLoginView, RegisterView
from registration.forms import LoginForm

urlpatterns = [
    path("", views.home, name="home"),
    # path("register", views.register_attempt, name="register_attempt"),
    # path("login", views.login_attempt, name="login_attempt"),
    path('login/', CustomLoginView.as_view(
        redirect_authenticated_user=True, 
        template_name='registration/login.html',
        authentication_form=LoginForm), name='login'),
    path('register/', RegisterView.as_view(), name='users-register'),
]
