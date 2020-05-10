from wxpusher import WxPusher

token = 'AT_dxgjVWxX6RThWd1QrfOokQBDBOHD6ag4'

def send_message(uids: list, content: str):
    """发送消息
    :param uid 用户的key
    :param content 内容
    """
    WxPusher.send_message(content,
                          uids=uids,
                          token=token)

# WxPusher.query_message('<messageId>')
def create_qrcode(username):
    """创建二维码
    :param extra 额外参数，可以用手机号
    """
    return WxPusher.create_qrcode(extra=username, token=token)
# WxPusher.query_user('<page>', '<page_size>', '<appToken>')