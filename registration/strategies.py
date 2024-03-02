import requests
from retrying import retry
from django.contrib.auth import login
from registration import helpers

class AuthStrategy:
    def prepare_auth_url(self, request):
        pass

    def social_auth_callback(self, request):
        pass


    def get_or_create_user(self, user_info):
        user = helpers.create_user(user_info)[0]
        helpers.update_profile(user)
        return user

    def login_user(self, request, user):
        login(request, user)

    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_api_call(self, url, headers):
        return requests.get(url, headers=headers)

    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def post_api_call(self, url, data, headers=None):
        return requests.post(url, headers=headers, data=data)
