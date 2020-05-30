from django.urls import path, include
# from rest_framework_jwt.views import obtain_jwt_token
from .views import SmsCodeViewSet, UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'authcode', SmsCodeViewSet, basename="authcode")
router.register(r'user', UserViewSet, basename="user")

urlpatterns = [
    path(r'api/', include(router.urls)),
]