import datetime
import json
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from rest_framework.views import APIView
from rest_framework import status, viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from autosign.sign import get_code as authcode
from .filters import SignRecordFilter
from .models import SignRecord
from .paginations import SignRecordPagination
from .serializers import SmsSerializer, UserSerializer, \
    UserDetailSerializer, SignRecordSerializer, WxPushSerializer
from .utils import create_qrcode, send_message
from .config import callback_key

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  viewsets.ReadOnlyModelViewSet,
                  viewsets.GenericViewSet, ):
    """创建用户, 获取用户基本信息, 用户登录"""

    # 序列化类
    serializer_class = UserSerializer
    # 过滤器
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SignRecordFilter
    # 权限验证
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    # 分页器
    pagination_class = SignRecordPagination

    def get_serializer_class(self):
        """根据条件使用对应的序列化器"""
        if self.action == "retrieve":
            # 获取用户实例
            return UserDetailSerializer
        elif self.action == "create":
            # 新建用户
            return UserSerializer
        elif self.action == "records":
            return SignRecordSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "records":
            return [permission() for permission in self.permission_classes]
        elif self.action == "create":
            return []
        return []

    def create(self, request, *args, **kwargs):
        """创建用户或登录"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['real_name'] = user.last_name
        re_dict["username"] = user.username
        last_login = user.last_login or user.date_joined
        re_dict["last_login"] = datetime.datetime.timestamp(last_login)
        re_dict["token"] = jwt_encode_handler(payload)
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_200_OK, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """获取用户基本信息"""

        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'id': kwargs['pk']})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def records(self, request, *args, **kwargs):
        """获取用户前5条签到记录"""

        queryset = self.filter_queryset(self.get_queryset(request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def qrcode(self, request, *args, **kwargs):
        """获取绑定的二维码"""
        extra = callback_key + '/' + request.user.username
        return Response(data=create_qrcode(json.dumps(extra)), status=status.HTTP_200_OK)

    def get_queryset(self, user=None):
        queryset = SignRecord.objects.all().filter(user_id=user)
        return queryset

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()


class SmsCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """发送手机短信验证码"""

    serializer_class = SmsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']
        if authcode(mobile):
            return Response(data={'msg': '验证码请求成功'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'msg': '验证码请求失败'}, status=status.HTTP_400_BAD_REQUEST)


class SignRecordViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """签到记录"""

    # 序列化类
    serializer_class = SignRecordSerializer
    # 过滤器
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SignRecordFilter
    # 查询集
    queryset = SignRecord.objects.all()
    # 权限认证
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, data=request.user)
        return Response(serializer.data)


class BindWxPushViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    """根据用户输入的key绑定推送"""

    serializer_class = WxPushSerializer
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def get_object(self):
        return self.request.user


class WxPushCallBackView(APIView):
    """留给wxpush的回调接口"""

    def post(self, request, format=None):
        data = json.loads(request.body)

        # 获取回调密钥，防止恶意利用
        # print(data)
        extra = data['data']['extra']
        key, username = extra.replace("\"", "").split('/') if '/' in extra else ('', '')
        if key != callback_key:
            return Response({'error': '此接口不对外开放'})

        if data.get('action', '') == 'app_subscribe':
            user = User.objects.filter(username=username).first()
            user.wxPushKey = data.get('data').get('uid', '')
            user.save()
            send_message(
                content='每日打卡消息会在此推送给您！\r\n如有问题，请联系qq1028813314',
                uids=[user.wxPushKey, ]
            )
            return Response({'status': True, 'message': '绑定成功'}, status=status.HTTP_200_OK)
