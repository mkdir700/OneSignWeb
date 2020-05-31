from rest_framework import serializers


class WxPushSerializer(serializers.Serializer):
    wx_push_key = serializers.CharField(
        required=True,
        error_messages={
            'required': 'wx_push_key必填'
        },
        help_text='用于绑定微信推送'
    )

    class Meta:
        fields = ['wx_push_key']

    def update(self, instance, validated_data):
        i = instance
        user = validated_data['user']
        user.wxPushKey = validated_data['wx_push_key']
        user.save()

    def validate(self, attrs):
        if not attrs['wx_push_key'].strip():
            serializers.ValidationError('')