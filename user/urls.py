from django.urls import path, include
# from rest_framework_jwt.views import obtain_jwt_token
from .views import SmsCodeViewSet, UserViewSet, BindWxPushViewSet, WxPushCallBackView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'authcode', SmsCodeViewSet, basename="authcode")
router.register(r'user', UserViewSet, basename="user")
router.register(r'wxpushkey', BindWxPushViewSet, basename="wxpushkey")

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'wxpushcallback', WxPushCallBackView.as_view(), name="wxpushcallback")
]