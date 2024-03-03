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
            'redirect_uri': request.build_absolute_uri(
                '/registration/social-auth-callback/?provider=google'
            ),
            'grant_type': 'authorization_code',
        }

        try:
            response = self.post_api_call(token_url, data=token_params)
            token_data = response.json()
        except Exception as e:
            raise Exception(f'[Google] token could not fetch {e}')

        # Use the access token to retrieve user information
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
        try:
            response = self.get_api_call(user_info_url, headers)
        except Exception as e:
            raise Exception(f'[Google] user info could not fetch {e}')

        user_info = response.json()

        if user_info:
            user = self.get_or_create_user(user_info)
            self.login_user(request, user)


class GitHubStrategy(AuthStrategy):
    def prepare_auth_url(self, request):
        github_auth_url = (
            f'https://github.com/login/oauth/authorize?'
            f'client_id={settings.GITHUB_CLIENT_ID}&'
            f'redirect_uri={request.build_absolute_uri("/registration/social-auth-callback/?provider=gitHub")}&'
            'scope=user'
        )
        return github_auth_url

    def social_auth_callback(self, request):
        code = request.GET.get('code')

        token_url = 'https://github.com/login/oauth/access_token'
        token_params = {
            'code': code,
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'redirect_uri': request.build_absolute_uri(
                '/registration/social-auth-callback/?provider=gitHub'
            ),
        }
        headers = {'Accept': 'application/json'}

        try:
            response = self.post_api_call(token_url, data=token_params, headers=headers)
            token_data = response.json()
        except Exception as e:
            raise Exception(f'[GitHub] token could not fetch {e}')

        access_token = token_data['access_token']

        user_info_url = 'https://api.github.com/user'
        email_info_url = 'https://api.github.com/user/emails'
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            user_info_response = self.get_api_call(user_info_url, headers)
            user_info = user_info_response.json()

            email_info_response = self.get_api_call(email_info_url, headers)
            email_info = email_info_response.json()
        except Exception as e:
            raise Exception(f'[Github] user info could not fetch {e}')

        primary_email = list(filter(lambda x: x['primary'] is True, email_info))

        if primary_email[0]:
            user_info['email'] = primary_email[0].get('email')
        else:
            raise Exception('Sorry, we could not your email via GitHub')

        if user_info:
            user = self.get_or_create_user(user_info)
            self.login_user(request, user)
