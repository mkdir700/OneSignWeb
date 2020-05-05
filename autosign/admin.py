from django.contrib import admin
from autosign.models import SignTasks


@admin.register(SignTasks)
class SignTasksAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active']