from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class LoginForm(forms.Form):
    """登录表单"""
    tel = forms.CharField(
        label="电话号码",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'}
        ),
        max_length=11
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入验证码'
            }
        ),
        max_length=6
    )

    def clean(self):
        tel = self.cleaned_data['tel']
        code = self.cleaned_data['code']


class BindEmailForm(forms.Form):
    email = forms.EmailField(
        label="邮箱",
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入您的邮箱'
            }
        )
    )
    auth_code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入邮箱验证码'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated:
            raise forms.ValidationError("未登录")

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError("邮箱不能为空")
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱已被使用")
        # TODO 换绑
        return email

    def clean_auth_code(self):
        raw_code = self.request.session.get('bind_email_code', '')
        receive_code = self.cleaned_data.get('auth_code', '')
        if not raw_code or not receive_code:
            raise forms.ValidationError('验证码不能为空')
        if raw_code != receive_code:
            raise forms.ValidationError('验证码不正确')
        return receive_code