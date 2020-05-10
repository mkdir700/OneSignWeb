from django.urls import path
from .views import pushCallBack, get_qrcode_for_user


urlpatterns = [
    path('callBack/', pushCallBack),
    path('qrcode/', get_qrcode_for_user, name='get_qrcode_for_user'),
]