import time
import string
import random
import datetime
from django.contrib import auth
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from .sign import cloud_run, local_run
from .sign import get_code as authcode
from .models import SignRecord
from .forms import BindEmailForm
from autosign.models import SignTasks
from autosign.exec_sign_task import start_run


# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# 每天8点半执行这个任务
# @register_job(scheduler, 'interval', id='autosign', seconds=10, args=['test'])
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
        data = {}
        # 请求签到链接，以此判断是否正确
        if user:
            # 校验成功后的两种情况：
            auth.login(request, user)
            # 添加本次签到记录
            SignRecord(user=user).save()
            # 将用户添加到任务表中
            if not SignTasks.objects.filter(user=user).exists():
                SignTasks(user=user).save()
            data['status'] = 'SUCCESS'
        else:
            data['status'] = 'ERROR'
        return JsonResponse(data)
    context = {}
    context['is_login'] = True if request.user.is_authenticated else False
    return render(request, 'login.html', context)


def center(request):
    """用户中心"""
    user = request.user
    if user.is_authenticated:
        context = {}

        ten_day_timestamp = 864000
        expire_time = user.last_login.timestamp() + ten_day_timestamp
        differ = expire_time - time.time()
        percent = '%.2f%%' % ((differ / ten_day_timestamp) * 100)
        context['expire_time'] = time.strftime("%Y-%m-%d %H:%M", time.localtime(expire_time))
        context['percent'] = percent


        now = datetime.datetime.now()
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        # 获取23:59:59
        lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
        context['records'] = SignRecord.objects.filter(user=user)[:5]
        context['is_sign_today'] = SignRecord.objects.filter(sign_time__range=(zeroToday, lastToday)).exists()
        return render(request, 'center.html', context)
    else:
        return redirect(reverse('login'))


def bind_email(request):
    """绑定邮箱"""
    data = {}
    redirect_to = reverse('center')
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = request.user
            user.email = email
            user.save()
            del request.session['bind_email_code']
            del request.session['send_code_time']
            # TODO 提示绑定成功
            data['status'] = 'SUCCESS'
        else:
            data['status'] = 'ERROR'
        return JsonResponse(data)
    else:
        form = BindEmailForm()
    context = {}
    context['form'] = form
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['return_back_url'] = redirect_to
    context['submit_text'] = '提交'
    return render(request, 'bind_email.html', context)


def send_code_by_email(request):
    """发送邮件验证码"""
    email = request.GET.get('email', '').strip()
    send_for = request.GET.get('send_for', '')
    data = {}
    if email:
        code = ''.join(random.sample(string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
            data['msg'] = '验证码请求频率过快，请稍等'
        else:
            request.session['bind_email_code'] = code
            request.session['send_code_time'] = now
            # 发送邮件
            send_mail(
                '邮箱绑定',
                '验证码：%s' % code,
                '1028813314@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
            data['msg'] = '验证码发送成功，请注意查收'
    else:
        data['msg'] = '验证码请求失败，请重新获取'
        data['status'] = 'ERROR'
    return JsonResponse(data)


def get_code(request):
    """请求手机验证码"""
    tel = request.GET.get('tel')
    data = {}
    if authcode(tel):
        data['status'] = 'SUCCESS'
        data['msg'] = '验证码发送成功，请注意查收'
    else:
        data['status'] = 'ERROR'
        data['msg'] = '验证码请求失败，请重新获取'
    return JsonResponse(data)


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
