from django.urls import path, include
from .views import pushCallBack, get_qrcode_for_user
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('callBack/', pushCallBack),
]
