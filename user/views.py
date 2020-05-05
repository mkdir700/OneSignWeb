import datetime
from django.contrib import auth
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from .sign import cloud_run
from .sign import get_code as authcode
from .models import SignRecord
from autosign.models import SignTasks

from autosign.exec_sign_task import start_run
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# 每天8点半执行这个任务
@register_job(scheduler, 'cron', id='autosign', hour=0, minute=2, args=['test'])
def test(test):
    # 具体要执行的代码
    print("执行打卡")
    start_run()


# 注册定时任务并开始
register_events(scheduler)
scheduler.start()

User = get_user_model()


def _sign(tel, code):
    """实现签到，并且返回cookie的值"""
    return cloud_run(tel, code)


@csrf_exempt
def login(request):
    # 得到电话号码和验证码
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(request, username=username, password=password)
        # 请求签到链接，以此判断是否正确
        if user:
            # 校验成功后的两种情况：
            auth.login(request, user)
            # 添加本次签到记录
            SignRecord(user=user).save()
            # 将用户添加到任务表中
            if not SignTasks.objects.filter(user=user).exists():
                SignTasks(user=user).save()
            return redirect(reverse('center'))
    return render(request, 'login.html')


def center(request):
    """用户中心"""
    user = request.user
    if user.is_authenticated:
        context = {}
        now = datetime.datetime.now()
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        # 获取23:59:59
        lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
        context['records'] = SignRecord.objects.filter(user=user)
        context['is_sign_today'] = SignRecord.objects.filter(sign_time__range=(zeroToday, lastToday)).exists()
        return render(request, 'center.html', context)
    else:
        return redirect(reverse('login'))


def get_code(request):
    """请求手机验证码"""
    tel = request.GET.get('tel')
    authcode(tel)
    data = {}
    data['status'] = 'SUCCESS'
    data['msg'] = '验证码发送成功，请注意查收'
    return JsonResponse(data)
