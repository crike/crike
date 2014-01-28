#coding:utf8
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


from models import *


class UploadFileForm(forms.Form):
    book = forms.CharField(max_length=50)
    lesson = forms.CharField(max_length=50)
    file  = forms.FileField()

class AddWordForm(forms.Form):
    name = forms.CharField(max_length=50)
    phonetics = forms.CharField(max_length=50, required=False)
    mean = forms.CharField(widget=forms.Textarea, required=False)
    audio  = forms.FileField(required=False)
    image0  = forms.FileField(required=False)
    image1  = forms.FileField(required=False)
    image2  = forms.FileField(required=False)

class CrikeRegistrationForm(forms.Form):
    required_css_class = 'required'

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                label=_("用户名"),
                                error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("邮箱"))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("密码"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("密码 (重复)"))
    is_human = forms.NullBooleanField(label=_("你是人类吗？"), required=False)
    school = forms.CharField(max_length=50,
                             label=_("学校"), required=False)
    dob = forms.DateField(label=_("生日 (例子: 1999-2-19)"), required=False)
    phone = forms.CharField(label=_("手机"), required=False)
    gender = forms.CharField(label=_("性别"), required=False)

    def clean_username(self):
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class CrikeLoginForm(forms.Form):
    pass


class UploadHeadSculptureForm(forms.Form):
    image = forms.ImageField(label=_('上传图片'))

