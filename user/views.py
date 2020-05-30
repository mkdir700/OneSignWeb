from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .models import SignRecord
from .serializers import SmsSerializer, UserSerializer, UserDetailSerializer, SignRecordSerializer
from autosign.sign import get_code as authcode

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  viewsets.ReadOnlyModelViewSet,
                  viewsets.GenericViewSet,):
    serializer_class = UserSerializer
    # 用户登录的情况下,才能继续下面的操作
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

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
        # 创建用户
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['real_name'] = user.last_name
        re_dict["username"] = user.username
        re_dict["last_login"] = user.last_login or user.date_joined
        re_dict["token"] = jwt_encode_handler(payload)
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_200_OK, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'id': kwargs['pk']})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def records(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, user=None):
        queryset = SignRecord.objects.all().filter(user_id=user)
        return queryset

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()


class SmsCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
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
    serializer_class = SignRecordSerializer
    queryset = SignRecord.objects.all()
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, data=request.user)
        return Response(serializer.data)
