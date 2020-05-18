from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


# 创建用户方法二: 捕获post_save信号后,进行存入处理
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=None, **kwargs):
    if created:
        instance.save()
        # 然后设置app ,覆写ready方法
