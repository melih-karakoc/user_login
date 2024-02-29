from django.urls import path, re_path, include
from . import views 
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from registration.views import CustomLoginView, RegisterView, home, profile
from registration.forms import LoginForm

urlpatterns = [
    # path("register", views.register_attempt, name="register_attempt"),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('login/', CustomLoginView.as_view(
        redirect_authenticated_user=True, 
        template_name='registration/login.html',
        authentication_form=LoginForm), name='login'),
    path('register/', RegisterView.as_view(), name='registration-register'),
    path('profile/', profile, name='registration-profile'),

]
