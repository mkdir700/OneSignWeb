from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from autosign.sign import get_code as authcode

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin):
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    # 用户登录的情况下,才能继续下面的操作
    permission_classes = [IsAuthenticated]

    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        """根据条件使用对应的序列化器"""
        if self.action == "retrieve":
            # 获取一用户实例
            return UserDetailSerializer
        elif self.action == "create":
            # 新建用户
            return UserRegSerializer
        elif self.action == "update":
            return UserRegSerializer
        return UserRegSerializer

    def get_permissions(self):
        if self.action == "retrieve":
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
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["username"] = user.username
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = self.perform_update(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["username"] = user.username
        # headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED)

    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
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
