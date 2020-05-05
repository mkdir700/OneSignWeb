from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class CustomModelBackends(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            user = UserModel.objects.create_user(username=username, tel=username)
        if user.is_staff:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            res = user.check_verify_code(username, password)
            if res['status'] and self.user_can_authenticate(user):
                user.cookie = res['cookies']
                user.save()
                return user
