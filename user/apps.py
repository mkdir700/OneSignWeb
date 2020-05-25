from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'user'
    verbose_name = '用户模块'
    #
    # def ready(self):
    #     import user.signals