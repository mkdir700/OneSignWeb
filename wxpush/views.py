import json
from user.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import create_qrcode


@csrf_exempt
def pushCallBack(request):
    """wxpush的回调函数
    保存用户的key
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action', '')
        if action == 'app_subscribe':
            username = data.get('data').get('extra', '')
            user = User.objects.get(username=username)
            user.wxPushKey = data.get('data').get('uid', '')
            user.save()
            return JsonResponse({'status': True})
    return JsonResponse({'status': False})

def get_qrcode_for_user(request):
    user = request.user
    if user.is_authenticated:
        resp = create_qrcode(user.username)
        return JsonResponse(resp)