from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from rest_framework import mixins
from .serializers import SmsSerializer, UserRegSerializer
from autosign.sign import get_code as authcode


User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)



    def perform_create(self, serializer):
        return serializer.save()
    # def create(self, request, *args, **kwargs):
    #     """添加用户"""
    #     pass
    # def get(self):
    #     """返回登录
    #     is_login: 是否登录
    #     """
    #     pass
    #
    # def post(self):
    #     """登录请求"""
    #     pass


class UserCenterView(APIView):

    def get(self):
        pass


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