from django.urls import path
from . import views


urlpatterns = [
    # path('bindEmail/', views.bind_email, name="bindEmail"),
    path('login/', views.login, name='login'),
    path('center/', views.center, name='center'),
    path('sendTelCode/', views.send_code_by_tel, name='sendTelCode'),
    # path('sendEmailCode/', views.send_code_by_email, name='sendEmailCode'),
]