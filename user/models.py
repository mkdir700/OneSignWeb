from django.db import models
from django.contrib.auth.models import AbstractUser
from .sign import cloud_run


class User(AbstractUser):
    # 电话号码
    tel = models.CharField(max_length=11, verbose_name="电话号码")
    # cookie
    cookie = models.TextField(default='')
    # wxPushKey
    wxPushKey = models.CharField(max_length=50, default='', verbose_name='消息Key')

    def __str__(self):
        return self.tel

    class Meta(AbstractUser.Meta):
        pass

    def check_verify_code(self, username, password):
        return cloud_run(username, password)


class SignRecord(models.Model):
    sign_time = models.DateTimeField(auto_now_add=True, verbose_name="打卡时间")
    sign_active = models.BooleanField(default=True, verbose_name="打卡状态")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta():
        verbose_name = '签到记录'
        verbose_name_plural = verbose_name
        ordering = ['-sign_time']