from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from .views import SmsCodeViewSet, UserViewSet
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sendTelCode', SmsCodeViewSet, basename="sendTelCode")
router.register(r'users', UserViewSet, basename="users")

urlpatterns = [
    # path('login/', views.login, name='login'),
    # path('center/', views.center, name='center'),
    # path('sendTelCode/', views.send_code_by_tel, name='sendTelCode'),
    path(r'login/', obtain_jwt_token),
    path(r'api/', include(router.urls)),
]