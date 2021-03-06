import datetime
from django.db import close_old_connections
from django.db.models import Q
from autosign.sign import local_run
from user.models import SignRecord, User
from user.utils import send_message


def handle_db_connections(func):
    def func_wrapper():
        close_old_connections()
        result = func()
        close_old_connections()
        return result

    return func_wrapper


@handle_db_connections
def perform_sign_task():
    """开始签到任务"""
    # 取出所有开启自动打卡的用户
    users = User.objects.filter(Q(is_auto_sign=True) & Q(is_superuser=False))
    for user in users:
        # user = User.objects.get(id=task.user_id)
        res = local_run(user.cookie)
        # 记录签到日志
        if res['status']:
            SignRecord(user=user, sign_active=True).save()
            content = '用户' + user.username + '\r\n今日健康码打卡消息来啦！\r\n' + '健康码自动打卡成功'
        else:
            SignRecord(user=user, sign_active=False).save()
            content = 'cookie失效,自动打卡失败\n请进入网站 http://one.z2blog.com 更新cookie'
        if user.wxPushKey:
            send_message(
                content=content,
                uids=[user.wxPushKey, ],
            )
    print("=======全部用户打卡已完成!=======")


@handle_db_connections
def remind_invalidated_cookies():
    """推送消息给cookie即将失效的用户"""
    now = datetime.datetime.now()
    # 明天的0点时间
    zero_tomorrow = now + datetime.timedelta(days=1, hours=-now.hour, minutes=-now.minute + 2, seconds=-now.second,
                                             microseconds=-now.microsecond)
    user_list = User.objects.filter(cookie_expired_time__lt=zero_tomorrow)
    for user in user_list:
        if user.wxPushKey:
            send_message(
                content='您的cookie即将失效,明日自动签到将失败\n请登录 http://one.z2blog.com 更新cookie',
                uids=[user.wxPushKey, ],
            )
