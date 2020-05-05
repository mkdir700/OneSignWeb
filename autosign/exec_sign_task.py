import time
from user.sign import local_run
from .models import SignTasks, User
from user.models import SignRecord



def start_run():
    """开始任务"""
    tasks = SignTasks.objects.filter(is_active=True)
    for task in tasks:
        user = User.objects.get(id=task.user_id)
        try:
            res = local_run(user.cookie)
            # 记录签到日志
            if res['status']:
                SignRecord(user=user).save()
        except:
            SignRecord(user=user, sign_active=False).save()
        time.sleep(1)


# def start_s_run(kwargs):
#     user = kwargs['user']
#     try:
#         print(111111111111111)
#         res = local_run(user.cookie)
#         # 记录签到日志
#         if res['status']:
#             SignRecord(user=user).save()
#     except:
#         SignRecord(user=user, sign_active=False).save()
