from django.contrib import admin
from .models import User, SignRecord


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'username', 'is_active']
    ordering = ("-id",)
    list_display_links = ['last_name', 'username']


@admin.register(SignRecord)
class SignRecordAdmin(admin.ModelAdmin):
    list_display = ['username', 'sign_time', 'sign_active']
    ordering = ('-id',)
