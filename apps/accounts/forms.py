from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import ApplicationUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '••••••••',
        'class': 'form-input',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '••••••••',
        'class': 'form-input',
    }))
    referral_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'كود الإحالة (اختياري)',
        'class': 'form-input',
    }))

    class Meta:
        model = ApplicationUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'اسم المستخدم', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'البريد الإلكتروني', 'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+201000000000', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'كلمتا المرور غير متطابقتين')

        if password:
            validate_password(password)

        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'اسم المستخدم أو البريد الإلكتروني',
        'class': 'form-input',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '••••••••',
        'class': 'form-input',
    }))
