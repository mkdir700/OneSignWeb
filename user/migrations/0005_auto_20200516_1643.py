# Generated by Django 3.0.3 on 2020-05-16 16:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_user_cookie_expired_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cookie_expired_time',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 6, 16, 43, 52, 971257), verbose_name='cookie失效时间'),
        ),
    ]