import os
import sys


pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + '../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HeathSignWeb.settings')

import django
django.setup()
from user.models import User
from autosign.sign import *


class HeathSignCustom(HeathSign):

    def get_user_info(self):
        url = 'https://www.ioteams.com/ncov/api/users/healthDetail'
        r = self.session.get(url, headers=self.headers)
        data = json.loads(r.text)
        # print(data)
        return data


users = User.objects.all()
user_list = []
for user in users:
    if user.cookie_is_valid():
        user_list.append(user)


for u in user_list:
    s = HeathSignCustom()
    if not s.cookie_login(u.cookie):
        continue
    data = s.get_user_info()
    u.last_name = data['data']['data']['userName']
    u.save()
