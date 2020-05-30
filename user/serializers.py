import re
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from HeathSignWeb import settings
from user.models import SignRecord

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """短信验证码"""
    mobile = serializers.CharField(max_length=11, required=True)

    def validate_mobile(self, mobile):
        """验证手机是否有效"""
        if not re.match(settings.REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码不合法")
        return mobile


class UserSerializer(serializers.ModelSerializer):
    """用户手机号码注册序列化器"""
    code = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        write_only=True,
        error_messages={
            'blank': '验证码不能为空',
            'required': '请输入验证码',
            'max_length': '验证码长度错误',
            'min_length': '验证码长度错误',
        },
        help_text='验证码')
    username = serializers.CharField(
        required=True,
        min_length=11,
        max_length=11,
        error_messages={
            'blank': '手机号码不能为空',
            'required': '手机号码不能为空',
            'max_length': '验证码长度错误',
            'min_length': '验证码长度错误',
        })

    class Meta:
        model = User
        fields = ['username', 'code']

    # 创建用户方法一: 在序列化器内重写create方法
    def create(self, validated_data):
        if User.objects.filter(username=validated_data['username']).exists():
            # 已存在用户
            user = validated_data['user']
            # TODO 更新用户名
            user.last_name = validated_data['info']['data']['data']['userName']
            # 更新cookie
            user.cookie = validated_data['cookie']
            # 更新last_time
            user.last_login = timezone.now()
            user.save()
            user.update_cookie_expire_time()
            return user
        else:
            # 不存在，创建用户
            return User.objects.create_user(
                username=validated_data['username'],
                tel=validated_data['username'],
                cookie=validated_data['cookie'],
                last_name=validated_data['info']['data']['data']['userName'])

    def validated_username(self, username):
        """验证手机是否有效"""
        # 验证手机号码是否合法
        if not re.match(settings.REGEX_MOBILE, username):
            raise serializers.ValidationError("手机号码不合法")
        return username

    def validate(self, attrs):
        """验证登录"""
        # if not User.objects.filter(username=attrs['username']).exists():
        # 用户不存在,需要去验证是否登录成功
        res = User.check_verify_code(self, attrs['username'], attrs['code'])
        if res['status']:
            attrs['user'] = User.objects.filter(
                username=attrs['username']).first()
            attrs['cookie'] = res['cookies']
            attrs['info'] = res['info']
        else:
            raise serializers.ValidationError("登录失败,请稍后再试")
        del attrs['code']
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(
        required=True,
        error_messages={
            'blank': '不能为空',
            'required': '用户id必填'
        }
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'wxPushKey', 'cookie_expired_time', 'is_today']

    def validate(self, attrs):
        user = User.objects.filter(id=attrs['id']).first()
        # 默认输出前6条记录
        attrs['records'] = SignRecord.objects.filter(user=user)[:6]
        # 今日打卡状态
        attrs['is_today'] = SignRecord.objects.filter(id=attrs['id']).last()
