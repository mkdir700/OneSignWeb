import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from HeathSignWeb import settings

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11, required=True)

    def validate_mobile(self, mobile):
        """验证手机是否有效"""
        # 验证手机号码是否合法
        if not re.match(settings.REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码不合法")
        return mobile


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=6, min_length=6, write_only=True,
                                 error_messages={
                                     'blank': '验证码不能为空',
                                     'required': '请输入验证码',
                                     'max_length': '验证码长度错误',
                                     'min_length': '验证码长度错误',
                                 },
                                 help_text='验证码')

    class Meta:
        model = User
        fields = ['username', 'code']

    # 创建用户方法一: 在序列化器内重写create方法
    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'], tel=validated_data['username'],
                                        cookie=validated_data['cookie'])

    def validate(self, attrs):
        """验证手机号码"""
        if not User.objects.filter(username=attrs['username']).exists():
            # 用户不存在,需要去验证是否登录成功
            res = User.check_verify_code(self, attrs['username'], attrs['code'])
            if res['status']:
                attrs['cookie'] = res['cookies']
            else:
                raise serializers.ValidationError("登录失败,请稍后再试")
        del attrs['code']
        return attrs
