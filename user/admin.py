from django.contrib import admin
from .models import User, SignRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'username', 'is_active']
    ordering = ("-id",)


@admin.register(SignRecord)
class SignRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'sign_time', 'sign_active']
    ordering = ('-id',)
