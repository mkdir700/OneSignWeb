from django.urls import path
from . import views

urlpatterns = [
    path('cookieSign/', views.sign_by_cookie, name='cookieSign'),
]