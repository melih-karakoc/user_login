from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView

from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm

def home(request):
    template = loader.get_template("registration/home.html")
    return HttpResponse(template.render(None, request)) 

def login_attempt(request):
    template = loader.get_template("registration/register.html")
    return HttpResponse(template.render(None, request)) 

def register_attempt(request):
    template = loader.get_template("registration/login.html")
    return HttpResponse(template.render(None, request)) 

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)
