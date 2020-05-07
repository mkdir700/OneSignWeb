import os
import json
import requests
import base64
# from config import *

COOKIES_PATH = ''


def encrypt_tel(tel):
    """加密手机号码"""
    encode_tel = base64.b64encode(tel.encode('utf-8'))
    base64_tel = encode_tel.decode('utf-8')
    base64_tel = base64_tel[::-1]
    base64_tel = base64_tel.replace("=", "1")
    return base64_tel


def get_code(tel) -> bool:
    """请求获取验证码"""
    auth_url = 'https://www.ioteams.com/ncov/api/users/authcode'
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

    def tel_login(self, tel, authcode) -> bool:
        """手机登录"""
        # 加密方式：base64加密，“=” 替换为 1，再进行反转
        base64_tel = encrypt_tel(tel)
        login_api = 'https://www.ioteams.com/ncov/api/users/general/login'
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
        res = json.loads(response.text)

        # 通过登录获取到company，以及ncov-access-token
        if res["code"] == 0:
            ncov_access_token = res['data']['meta']['access-token']
            company = res['data']['data']['users'][0]['companyCode']
            headers["ncov-access-token"] = ncov_access_token
            payload = "company={}&type={}".format(company, "h5")
            response = self.session.request(
                "POST",
                "https://www.ioteams.com/ncov/api/users/companies/switch",
                headers=headers,
                data=payload)
        else:
            return False
        return True

    def cookie_login(self, cookies):
        """通过cookie登录"""
        self.set_cookies(cookies)
        r = self.session.get(
            'https://www.ioteams.com/ncov/api/sys/user/info',
            headers=self.headers)
        if r.status_code == 200:
            # 失效cookies
            return True
        else:
            return False

    def __save_cookies(self):
        """保存cookies"""
        cookies = self.session.cookies.get_dict()
        cookies["ncov-access-token-health-user"] = cookies["ncov-access-token-h5"]
        self.headers["ncov-access-token"] = cookies["ncov-access-token-h5"]
        self.session.cookies.set(
            "ncov-access-token-health-user",
            cookies["ncov-access-token-h5"])
        return json.dumps(cookies)

    def set_cookies(self, cookies):
        """设置cookies"""
        # cookies有效期10天
        cookies = json.loads(cookies)
        self.headers["ncov-access-token"] = cookies["ncov-access-token-h5"]
        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)

    def check_cookies(self, cookies):
        """检测cookies是否存在且是否有效"""
        # 设置cookies
        self.set_cookies(cookies)
        r = self.session.get(
            'https://www.ioteams.com/ncov/api/sys/user/info',
            headers=self.headers)
        if r.status_code == 200:
            # 失效cookies
            return True
        else:
            return False

    def __server_send(self, dict):
        """server酱将消息推送至微信"""
        params = {
            'text': '健康码每日自动打卡消息！',
            'desp': dict['detail']
        }

        requests.get('', params=params)

    def __get_user_info(self):
        """获取个人信息"""
        url = 'https://www.ioteams.com/ncov/api/users/healthDetail'
        r = self.session.get(url, headers=self.headers)
        data = json.loads(r.text)
        # 获取上次上报信息以及用户唯一标识符
        self.user_id = data["data"]["data"]["_id"]
        self.latestReport = data["data"]["data"]["latestReport"]
        address = data["data"]["data"]["address"]
        # todo 部分用户取不到lastHealthReport
        try:
            lastHealthReport = data["data"]["data"]["lastHealthReport"]
        except:
            lastHealthReport = {
                'self_confirmed': False,
                'self_suspected': False,
                'family_suspected': False,
                'family_confirmed': False,
                'infected': False,
                'contacted': False,
                'fever': False}
        address.pop("detail")
        address.pop("_id")
        fields = [
            "isInitCreate",
            "remoteHealthLevel",
            "_id",
            "temperature",
            "company",
            "user",
            "created_at",
            "updated_at",
            "__v",
            "current_fever"]
        for field in fields:
            try:
                lastHealthReport.pop(field)
            except BaseException:
                continue
        lastHealthReport["description"] = ""
        lastHealthReport["at_home"] = True
        # 数据整理
        self.last_report_msg = {"address": address}
        self.last_report_msg.update(lastHealthReport)

    def __daily_reports(self):
        """每日信息上报"""
        url = 'https://www.ioteams.com/ncov/api/users/dailyReport'
        r = self.session.post(
            url, headers=self.headers, data=json.dumps(
                self.last_report_msg))
        r = json.loads(r.text)
        if r['msg'] == 'success':
            print('上报信息成功!')
            return {'msg': True, 'detail': '今日信息上报成功'}
        else:
            print(r['msg'])
            return {'msg': False, 'detail': r['msg']}

    def __health_report(self):
        """健康码打卡"""
        data = {
            'current_fever': False,
            'temperature': 36.5
        }
        url = 'https://www.ioteams.com/ncov/api/users/{}/health-report'.format(
            self.user_id)
        r = requests.patch(url, headers=self.headers, data=json.dumps(data))
        if r.status_code == 204:
            print("打卡成功")
            return {'msg': True, 'detail': '健康码打卡成功'}
        else:
            print("打卡失败")
            return {'msg': False, 'detail': '健康码打卡失败'}

    def run(self) -> dict:
        cookies = self.__save_cookies()
        self.__get_user_info()

        h1 = self.__daily_reports()
        h2 = self.__health_report()

        msg = {
            'code': 100,
            'status': True,
            'detail': h1['detail'] + '\r\r' + h2['detail'],
            'cookies': cookies
        }
        # self.__server_send(msg)
        return msg


def local_run(cookie):
    """本地挂机运行"""
    s = HeathSign()
    if not s.cookie_login(cookie):
        return {'status': False, 'msg': "cookie可能失效"}
    return s.run()


def cloud_run(tel, code) -> dict:
    """提供给前端手动签到"""
    s = HeathSign()
    if not s.tel_login(tel, code):
        return {'status': False, 'msg': "登录失败"}
    return s.run()
