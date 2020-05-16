from django.http import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from .sign import local_run
from .exec_sign_task import to_sign_in_task, to_remind_cookie_failure


# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# @register_job(scheduler, 'interval', id='autosign', seconds=11)
@register_job(scheduler, 'cron', id='autosign', hour=0, minute=2)
def autosign():
    # 具体要执行的代码
    print("执行打卡")
    to_sign_in_task()


# @register_job(scheduler, 'interval', id='remind_cookie', seconds=11)
@register_job(scheduler, 'cron', id='remind_cookie', hour=6, minute=0)
def remind_cookie():
    to_remind_cookie_failure()


# 注册定时任务并开始
register_events(scheduler)
scheduler.start()


def sign_by_cookie(request):
    user = request.user
    data = {}
    if not user.is_authenticated:
        data['status'] = 'ERROR'
        data['msg'] = '用户未登录'
        return JsonResponse(data)
    resp = local_run(user.cookie)
    if resp['status']:
        data['status'] = 'SUCCESS'
        data['msg'] = '手动打卡成功'
    else:
        data['status'] = 'ERROR'
        data['msg'] = resp['msg']
    return JsonResponse(data)

