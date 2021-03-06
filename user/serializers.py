import re
import datetime
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from Core import settings
from user.models import SignRecord

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """短信验证码"""

    mobile = serializers.CharField(max_length=11, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def validate_mobile(self, mobile):
        """验证手机是否有效"""
        if not re.match(settings.REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码不合法")
        return mobile


class SignRecordSerializer(serializers.ModelSerializer):
    """签到记录序列化"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SignRecord
        fields = ['user', 'sign_time', 'sign_active']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
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
        help_text='验证码'
    )
    username = serializers.CharField(
        required=True,
        min_length=11,
        max_length=11,
        error_messages={
            'blank': '手机号码不能为空',
            'required': '手机号码不能为空',
            'max_length': '验证码长度错误',
            'min_length': '验证码长度错误',
        },
        help_text='手机号码'
    )

    class Meta:
        model = User
        fields = ['username', 'code']

    # 创建用户方法一: 在序列化器内重写create方法
    def create(self, validated_data):
        if User.objects.filter(username=validated_data['username']).exists():
            # 已存在用户
            user = validated_data['user']
            # TODO 更新真实姓名
            user.last_name = validated_data['info']['data']['data']['users'][0]['userName']
            user.cookie = validated_data['cookie']
            user.last_login = timezone.now()
            user.update_cookie_expire_time()
        else:
            # 不存在，创建用户
            user = User.objects.create_user(
                username=validated_data['username'],
                tel=validated_data['username'],
                cookie=validated_data['cookie'],
                last_name=validated_data['info']['data']['data']['users'][0]['userName'])
        # 新增本次打卡记录
        SignRecord.objects.create(user=user)
        return user

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
    """用户详细信息"""
    id = serializers.IntegerField(
        required=True,
        error_messages={
            'blank': '不能为空',
            'required': '用户id必须填写'
        },
        help_text='用户id'
    )
    real_name = serializers.SerializerMethodField()
    is_sign_today = serializers.SerializerMethodField()
    records = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    cookie_expired_time = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'wxPushKey', 'cookie_expired_time', 'real_name', 'is_sign_today',
                  'records']
        extra_kwargs = {
            'username': {'read_only': True},
        }

    @staticmethod
    def get_real_name(obj) -> str:
        return obj.last_name

    @staticmethod
    def get_is_sign_today(obj) -> bool:
        now = datetime.datetime.now()
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        # lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
        # return SignRecord.objects.filter(user=obj, sign_time__range=(zeroToday, now), sign_active=True).exists()
        return SignRecord.objects.filter(user=obj, sign_time__range=(zeroToday, now), sign_active=True).exists()

    @staticmethod
    def get_records(obj):
        # 默认输出前6条记录
        records = SignRecord.objects.filter(user=obj).values('id', 'sign_time', 'sign_active')[:5]
        new_records = []
        for record in records:
            record['sign_time'] = datetime.datetime.timestamp(record['sign_time'])
            new_records.append(record)
        return new_records

    @staticmethod
    def get_cookie_expired_time(obj):
        return datetime.datetime.timestamp(obj.cookie_expired_time)

    @staticmethod
    def get_last_login(obj):
        return datetime.datetime.timestamp(obj.date_joined if obj.date_joined else obj.last_login)


class WxPushSerializer(serializers.Serializer):
    wx_push_key = serializers.CharField(
        required=True,
        error_messages={
            'required': 'wx_push_key必填'
        },
        help_text='用于绑定微信推送',
        source='wxPushKey',  # source 是数据库字段
        write_only=True
    )

    class Meta:
        fields = ['wxPushKey']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.wxPushKey = validated_data['wxPushKey']
        instance.save()
        return instance
