from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleLoginForm(forms.Form):
    """Basit giriş formu"""
    username = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'E-posta adresiniz'
        })
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifreniz'
        })
    )


class SimpleRegisterForm(forms.Form):
    """Basit kayıt formu"""
    first_name = forms.CharField(
        label='Ad',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Adınız'
        })
    )
    last_name = forms.CharField(
        label='Soyad',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Soyadınız'
        })
    )
    email = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'E-posta adresiniz'
        })
    )
    password = forms.CharField(
        label='Şifre',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifreniz'
        })
    )
    user_type = forms.ChoiceField(
        label='Kullanıcı Tipi',
        choices=[
            ('jobseeker', 'İş Arayan'),
            ('business', 'İş Veren')
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'user-type-input'
        })
    )
    
