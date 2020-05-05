from django import forms


class LoginForm(forms.Form):
    """登录表单"""
    tel = forms.CharField(
        label="电话号码",
        widget=forms.CharField(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入用户名'}
        ),
        max_length=11
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.CharField(
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

