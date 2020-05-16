"""更新已有用户的cookie失效时间"""
import os
import sys
import datetime

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + '../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HeathSignWeb.settings')

import django
django.setup()
from user.models import User


users = User.objects.all()
for user in users:
    user.cookie_expired_time = datetime.datetime.fromtimestamp(user.last_login.timestamp() + 864000)
    user.save()
