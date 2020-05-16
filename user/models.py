import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from autosign.sign import cloud_run


# UserModel = get_user_model()


class User(AbstractUser):
    # 电话号码
    tel = models.CharField(max_length=11, verbose_name="电话号码")
    # cookie
    cookie = models.TextField(default='')
    # 默认为null,第一次登录的时候才去设置
    cookie_expired_time = models.DateTimeField(null=True, verbose_name='cookie失效时间')
    # wxPushKey
    wxPushKey = models.CharField(max_length=50, default='', verbose_name='消息Key')

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.tel

    @staticmethod
    def check_verify_code(username, password):
        return cloud_run(username, password)

    def update_cookie_expire_time(self):
        """更新cookie的失效时间"""
        expire_time_stamp = self.last_login.timestamp() + 864000
        cookie_expired_time = datetime.datetime.fromtimestamp(expire_time_stamp)
        self.cookie_expired_time = cookie_expired_time
        self.save()
        return cookie_expired_time


class SignRecord(models.Model):
    sign_time = models.DateTimeField(auto_now_add=True, verbose_name="打卡时间")
    sign_active = models.BooleanField(default=True, verbose_name="打卡状态")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '签到记录'
        verbose_name_plural = verbose_name
        ordering = ['-sign_time']