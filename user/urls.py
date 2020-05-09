from django.urls import path
from . import views


urlpatterns = [
    path('bindEmail/', views.bind_email, name="bindEmail"),
    path('login/', views.login, name='login'),
    path('center/', views.center, name='center'),
    path('get_code/', views.get_code, name='get_code'),
    path('sendEmailCode/', views.send_code_by_email, name='sendEmailCode'),
    path('cookieSign/', views.sign_by_cookie, name='cookieSign'),
]