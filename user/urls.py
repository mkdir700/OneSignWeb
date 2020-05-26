from django.urls import path, include
# from rest_framework_jwt.views import obtain_jwt_token
from .views import SmsCodeViewSet, UserViewSet
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sendTelCode', SmsCodeViewSet, basename="sendTelCode")
router.register(r'user', UserViewSet, basename="user")


urlpatterns = [
    path(r'api/', include(router.urls)),
]