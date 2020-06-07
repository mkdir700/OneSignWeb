import os
import json
import requests
import base64

HOST = "https://www.ioteams.com"


def encrypt_tel(tel):
    """加密手机号码"""
    encode_tel = base64.b64encode(tel.encode('utf-8'))
    base64_tel = encode_tel.decode('utf-8')
    base64_tel = base64_tel[::-1]
    base64_tel = base64_tel.replace("=", "1")
    return base64_tel


def get_code(tel) -> bool:
    """请求获取验证码"""
    auth_url = HOST+'/ncov/api/users/authcode'
    base64_tel = encrypt_tel(tel)
    payload = 'tel=' + base64_tel
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request(
        "POST", auth_url, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code == 204:
        print(response.text.encode('utf8'))
        print("验证码发送成功")
        return True
    else:
        print("验证码请求失败")
        return False


class HeathSign(object):

    def __init__(self):
        self.headers = {
            'Accept': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 '
                      'Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Host': 'www.ioteams.com',
            'Referer': 'https://www.ioteams.com/ncov/'}
        self.session = requests.session()
        self.user_id = ""
        self.after_login_info = {}

    def login_by_mobile(self, tel, authcode) -> bool:
        """手机登录"""
        # 加密方式：base64加密，“=” 替换为 1，再进行反转
        base64_tel = encrypt_tel(tel)
        login_api = HOST + '/ncov/api/users/general/login'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = "tel={}&mode=1&authcode={}&type=h5".format(
            base64_tel, authcode)
        response = self.session.request(
            "POST", login_api, headers=headers, data=payload)
        if response.status_code != 200:
            print("登录失败")
            return False
        # 保存请求登录后 拿到的信息
        self.after_login_info = json.loads(response.text)
        return self.set_headers()

    def set_headers(self):
        # 获取company及ncov-access-token, 并设置请求头
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if self.after_login_info["code"] == 0:
            ncov_access_token = self.after_login_info['data']['meta']['access-token']
            company = self.after_login_info['data']['data']['users'][0]['companyCode']
            headers["ncov-access-token"] = ncov_access_token
            payload = "company={}&type={}".format(company, "h5")
            self.session.request(
                "POST",
                HOST + "/ncov/api/users/companies/switch",
                headers=headers,
                data=payload)
            return True
        return False

    def login_by_cookies(self, cookies):
        """通过cookie登录"""
        self.set_cookies(cookies)
        r = self.session.get(
            HOST + '/ncov/api/sys/user/info',
            headers=self.headers)
        return True if r.status_code == 200 else False

    def _new_cookies(self) -> json:
        """处理本次登录的cookie并返回"""
        cookies = self.session.cookies.get_dict()
        cookies["ncov-access-token-health-user"] = cookies["ncov-access-token-h5"]
        self.headers["ncov-access-token"] = cookies["ncov-access-token-h5"]
        self.session.cookies.set(
            "ncov-access-token-health-user",
            cookies["ncov-access-token-h5"])
        return json.dumps(cookies)

    def set_cookies(self, cookies):
        """设置cookies"""
        cookies = json.loads(cookies)
        self.headers["ncov-access-token"] = cookies["ncov-access-token-h5"]
        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def get_last_report(self):
        """获取上次上报的信息"""
        lastHealthReport = {}
        r = self.session.get(HOST + '/ncov/api/users/last-report', headers=self.headers)
        data = json.loads(r.text)
        print(data)
        self.user_id = data['data']['data']['user']
        address = data['data']['data']['address']
        address.pop('_id')
        address.pop('province')
        print(address)

        # TODO 测试不修改这些字段，直接带着请求是否可行

        lastHealthReport['self_confirmed'] = False
        lastHealthReport['self_suspected'] = False
        lastHealthReport['family_suspected'] = False
        lastHealthReport['family_confirmed'] = False
        lastHealthReport['infected'] = False
        lastHealthReport['contacted'] = False
        lastHealthReport['fever'] = False
        lastHealthReport['description'] = False
        lastHealthReport['at_home'] = False
        lastHealthReport.update(address)
        return lastHealthReport

    def _daily_reports(self) -> bool:
        """每日信息上报"""
        last_report = self.get_last_report()
        url = HOST + '/ncov/api/users/dailyReport'
        r = self.session.post(
            url, headers=self.headers, data=json.dumps(
                last_report))
        r = json.loads(r.text)

        # TODO 检查请求成功后响应信息

        print(r, '1111111111')
        if r['msg'] == 'success':
            print('上报信息成功!')
            return True
        else:
            print(r['msg'])
            return False

    def _health_report(self) -> bool:
        """健康码打卡"""
        data = {
            'current_fever': False,
            'temperature': 36.5
        }
        url = HOST + '/ncov/api/users/{}/health-report'.format(
            self.user_id)
        r = requests.patch(url, headers=self.headers, data=json.dumps(data))
        print("健康码打卡成功")
        return True if r.status_code == 204 else False

    def run(self) -> dict:
        new_cookies = self._new_cookies()
        h1 = self._daily_reports()
        h2 = self._health_report()
        detail = ""
        if h1 and h2:
            detail = "今日健康信息【ok】\n健康码打卡【ok】"
        elif h2:
            detail = "健康码打卡成功"
        return {
            'code': 100,
            'status': True,
            'detail': detail,
            'cookies': new_cookies,
            'info': self.after_login_info
        }


def local_run(cookie) -> dict:
    """本地挂机运行"""
    s = HeathSign()
    if not s.login_by_cookies(cookie):
        return {'status': False, 'msg': "cookie已失效"}
    data = s.run()
    return data


def cloud_run(tel, code) -> dict:
    """提供给前端手动签到"""
    s = HeathSign()
    if not s.login_by_mobile(tel, code):
        return {'status': False, 'msg': "登录失败"}
    return s.run()
