from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class SignTasks(models.Model):
    """任务表

    每天取出所有的任务，依次执行签到任务
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, verbose_name="激活状态")

    class Meta():
        ordering = ['-id']