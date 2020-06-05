import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from autosign.sign import cloud_run


class User(AbstractUser):
    # 电话号码
    tel = models.CharField(max_length=11, verbose_name="电话号码")
    # cookie
    cookie = models.TextField(default='')
    # 默认为null,第一次登录的时候才去设置
    # date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    cookie_expired_time = models.DateTimeField(verbose_name='cookie失效时间', default=datetime.datetime.fromtimestamp(
        timezone.now().timestamp() + 864000))
    # wxPushKey
    wxPushKey = models.CharField(max_length=50, default='', verbose_name='消息Key')

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        return self.tel

    # @staticmethod
    def check_verify_code(self, username, password):
        return cloud_run(username, password)

    def cookie_is_valid(self) -> bool:
        """判断用户cookie当前是否有效"""
        now = datetime.datetime.now()
        # 明天的0点时间
        zero_tomorrow = now + datetime.timedelta(days=1, hours=-now.hour, minutes=-now.minute + 2, seconds=-now.second,
                                                 microseconds=-now.microsecond)
        return True if self.cookie_expired_time > zero_tomorrow else False
    cookie_is_valid.short_description = 'cookie是否有效'

    def wx_push_is_bind(self) -> bool:
        """用户是否绑定wxpush"""
        return True if self.wxPushKey else False
    wx_push_is_bind.short_description = '是否绑定wxPush'

    def update_cookie_expire_time(self):
        """更新cookie的失效时间"""
        self.cookie_expired_time = datetime.datetime.fromtimestamp(self.last_login.timestamp() + 864000)
        self.save()


class SignRecord(models.Model):
    sign_time = models.DateTimeField(auto_now_add=True, verbose_name="打卡时间")
    sign_active = models.BooleanField(default=True, verbose_name="打卡状态")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '签到记录'
        verbose_name_plural = verbose_name
        ordering = ['-sign_time']
