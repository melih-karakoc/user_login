from django.urls import path
from . import views 
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register_attempt, name="register_attempt"),
    path("login", views.login_attempt, name="login_attempt"),
]
