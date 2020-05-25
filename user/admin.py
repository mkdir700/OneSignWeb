import datetime
from django.contrib import admin
from .models import User, SignRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 新增cookie是否有效
    list_display = ['username', 'is_active', 'cookie_is_valid', 'wx_push_is_bind']
    ordering = ("-id",)


@admin.register(SignRecord)
class SignRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'sign_time', 'sign_active']
    ordering = ('-id',)
