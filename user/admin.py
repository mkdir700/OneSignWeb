from django.contrib import admin
from .models import User
from django_apscheduler.models import DjangoJob


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['tel', 'is_active']
    ordering = ("-id", )


# @admin.register(DjangoJob)
# class DjangoJobAdmin(admin.ModelAdmin):
#     list_display = ['id', ]

# class UserInline(admin.StackedInline):
#     model = User
#     can_delete = False
#
#
# class UserAdmin(BaseUserAdmin):
#     inlines = (UserInline, )
#     list_display = ['tel, is_active']
#
#     def tel(self, obj):
#         return obj.user.tel
#     tel.short_description = "电话号码"
#
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
#