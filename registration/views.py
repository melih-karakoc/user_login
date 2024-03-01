from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.views import View
from django.contrib.auth.models import User
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .forms import RegisterForm, LoginForm, UpdateUserForm
from .tasks import send_verification_email
from .helpers import TokenGenerator, create_user, send_verification_email, update_profile


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'registration/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        try:
            user = create_user(form)
            if user:
                send_verification_email(request, user)

                username = user.username
                messages.success(request, f'Account created for {username} please verify your email')
                return redirect(to='login')

            return render(request, self.template_name, {'form': form})
        except Exception as e:
            messages.warning(request, f'Something went wrong the reason: {e}')
            return render(request, 'registration/warning_page.html')


class CustomLoginView(LoginView):
    form_class = LoginForm
    verification_required_msg = "You should verify your email first"

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        user = form.get_user()

        if user.profile.is_email_verified != True:
            messages.success(self.request, self.verification_required_msg)
            template = 'registration/warning_page.html'
            return render(self.request, template)

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='registration-profile')
    else:
        user = request.user
        profile = user.profile
        user_form = UpdateUserForm(instance=user)

    return render(request, 'registration/profile.html', {'user_form': user_form, 'profile': profile })

@require_http_methods(["GET"])
def verify_email_confirm(request, uidb64, token):
    account_activation_token = TokenGenerator()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        try:
            update_profile(user)
        except Exception as e:
            messages.warning(request, f'User could not updated reason:{e}')
            return render(request, 'registration/warning_page.html')

        messages.success(request, 'Your email has been verified.')
        return redirect(to='login')   
    else:
        messages.warning(request, 'The link is invalid.')
        return render(request, 'registration/warning_page.html')

def home(request):
    template = loader.get_template("registration/home.html")
    return HttpResponse(template.render(None, request))
