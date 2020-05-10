from user.models import User
from django.shortcuts import render
from django.http import JsonResponse
from .utils import create_qrcode



def pushCallBack(request):
    """wxpush的回调函数
    保存用户的key
    """
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'app_subscribe':
            username = request.POST.get('extra', '')
            user = User.objects.get(username=username)
            user.wxPushKey = request.POST.get('uid', '')
            user.save()


def get_qrcode_for_user(request):
    user = request.user
    if user.is_authenticated:
        resp = create_qrcode(user.username)
        return JsonResponse(resp)