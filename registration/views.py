import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
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
            messages.info(self.request, self.verification_required_msg)
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

def initiate_social_auth(request):
    # Redirect the user to Google for authentication
    google_auth_url = (
        f'https://accounts.google.com/o/oauth2/auth?'
        f'client_id={settings.GOOGLE_CLIENT_ID}&'
        f'redirect_uri={request.build_absolute_uri("/registration/social-auth-callback/")}&'
        'response_type=code&'
        'scope=email profile'
    )
    return redirect(google_auth_url)

def social_auth_callback(request):
    # Handle the callback URL after authentication
    code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_url = 'https://oauth2.googleapis.com/token'
    token_params = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.build_absolute_uri('/registration/social-auth-callback/'),
        'grant_type': 'authorization_code',
    }

    response = requests.post(token_url, data=token_params)
    token_data = response.json()

    # Use the access token to retrieve user information
    user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    if user_info:
        user = create_user(user_info)[0]
        update_profile(user)
        login(request, user)

    return render(request, 'registration/home.html')
