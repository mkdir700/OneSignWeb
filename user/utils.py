from wxpusher import WxPusher
from .config import wxpush_token as token


def send_message(uids: list, content: str):
    """发送消息
    :param uids: 待接收消息用户id
    :param uid 用户的key
    :param content 内容
    """
    WxPusher.send_message(content,
                          uids=uids,
                          token=token)


def create_qrcode(username):
    """创建二维码
    :param username: 手机号码
    """
    return WxPusher.create_qrcode(extra=username, token=token)
# WxPusher.query_user('<page>', '<page_size>', '<appToken>')
