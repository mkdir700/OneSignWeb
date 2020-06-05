from wxpusher import WxPusher
# def jwt_response_payload_handler(token, user=None, request=None, role=None):
#
#     return {
#         'authenticated': 'true',
#         'username': user.username,
#         'token': token
#     }

token = 'AT_dxgjVWxX6RThWd1QrfOokQBDBOHD6ag4'


def send_message(uids: list, content: str):
    """发送消息
    :param uids: 待接收消息用户id
    :param uid 用户的key
    :param content 内容
    """
    WxPusher.send_message(content,
                          uids=uids,
                          token=token)

# WxPusher.query_message('<messageId>')


def create_qrcode(username):
    """创建二维码
    :param username: 手机号码
    """
    return WxPusher.create_qrcode(extra=username, token=token)
# WxPusher.query_user('<page>', '<page_size>', '<appToken>')
