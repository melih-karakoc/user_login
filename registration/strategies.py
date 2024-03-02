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
