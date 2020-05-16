import time
import datetime
from django.contrib import auth
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from autosign.sign import get_code as authcode
from .models import SignRecord
from autosign.models import SignTasks

User = get_user_model()


@csrf_exempt
def login(request):
    # 得到电话号码和验证码
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(request, username=username, password=password)
        # user.check_verify_code(username, password)
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
            # 更新易统计cookie失效时间
            user.update_cookie_expire_time()
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


def send_code_by_tel(request):
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
