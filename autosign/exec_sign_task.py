import time
from user.sign import local_run
from .models import SignTasks, User
from user.models import SignRecord
from wxpush.utils import send_message


def start_run():
    """开始任务"""
    tasks = SignTasks.objects.filter(is_active=True)
    sign_status = False
    for task in tasks:
        user = User.objects.get(id=task.user_id)
        try:
            res = local_run(user.cookie)
            # 记录签到日志
            if res['status']:
                SignRecord(user=user).save()
                sign_status = True
        except BaseException:
            SignRecord(user=user, sign_active=False).save()
        content = '用户' + user.username + '\r\n今日健康码打卡消息来啦！\r\n' + \
            '健康码自动打卡成功' if sign_status else '健康码自动打卡失败'
        if user.wxPushKey:
            send_message(
                content=content,
                uids=[user.wxPushKey, ],
            )
