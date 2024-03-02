import requests
from django.shortcuts import redirect
from django.conf import settings

from registration.strategies import AuthStrategy

class GoogleStrategy(AuthStrategy):
    def prepare_auth_url(self, request):
        google_auth_url = (
            f'https://accounts.google.com/o/oauth2/auth?'
            f'client_id={settings.GOOGLE_CLIENT_ID}&'
            f'redirect_uri={request.build_absolute_uri("/registration/social-auth-callback/?provider=google")}&'
            'response_type=code&'
            'scope=email profile'
        )
        return google_auth_url


    def social_auth_callback(self, request):
        # Handle the callback URL after authentication
        code = request.GET.get('code')

        # Exchange the authorization code for an access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_params = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': request.build_absolute_uri('/registration/social-auth-callback/?provider=google'),
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
            user = self.get_or_create_user(user_info)
            self.login_user(request, user)
