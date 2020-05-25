

def jwt_response_payload_handler(token, user=None, request=None, role=None):

    return {
        'authenticated': 'true',
        'username': user.username,
        'token': token
    }