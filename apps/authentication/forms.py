from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, JobSeekerProfile, BusinessProfile


class LoginForm(forms.Form):
    """Giriş formu"""
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'E-posta veya telefon numarası',
            'autocomplete': 'username'
        }),
        label='E-posta veya Telefon'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifre',
            'autocomplete': 'current-password'
        }),
        label='Şifre'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Beni hatırla'
    )


class RegisterForm(forms.ModelForm):
    """Kayıt formu"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifre'
        }),
        label='Şifre',
        min_length=8
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Şifre tekrar'
        }),
        label='Şifre Tekrar'
    )
    
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'user-type-input'
        }),
        label='Kullanıcı Tipi'
    )
    
    selected_plan = forms.ChoiceField(
        choices=CustomUser.PLAN_CHOICES,
        widget=forms.HiddenInput(),
        required=False,
        initial='free'
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label='Kullanım koşullarını kabul ediyorum'
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_type']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ad'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Soyad'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'E-posta adresi'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Telefon numarası'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Şifreler eşleşmiyor.')
        
        return password_confirm
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise ValidationError('Şifre en az 8 karakter olmalıdır.')
        
        if password.isdigit():
            raise ValidationError('Şifre sadece rakamlardan oluşamaz.')
        
        if password.isalpha():
            raise ValidationError('Şifre sadece harflerden oluşamaz.')
        
        return password


class JobSeekerRegistrationForm(forms.ModelForm):
    """İş arayan için ek kayıt bilgileri"""
    
    class Meta:
        model = JobSeekerProfile
        fields = ['city', 'experience_years']
        widgets = {
            'city': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_years': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class BusinessRegistrationForm(forms.ModelForm):
    """İş veren için ek kayıt bilgileri"""
    
    class Meta:
        model = BusinessProfile
        fields = ['company_name', 'contact_person', 'city', 'establishment_year']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Şirket adı'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Yetkili kişi'
            }),
            'city': forms.Select(attrs={
                'class': 'form-select'
            }),
            'establishment_year': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Profil güncelleme formu"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input'
            }),
        }


class JobSeekerProfileUpdateForm(forms.ModelForm):
    """İş arayan profil güncelleme"""
    
    class Meta:
        model = JobSeekerProfile
        fields = ['city', 'district', 'experience_years', 'bio', 'portfolio_url']
        widgets = {
            'city': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.TextInput(attrs={'class': 'form-input'}),
            'experience_years': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Kendinizi tanıtın...'
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://...'
            }),
        }


class BusinessProfileUpdateForm(forms.ModelForm):
    """İş veren profil güncelleme"""
    
    class Meta:
        model = BusinessProfile
        fields = [
            'company_name', 'company_description', 'company_size',
            'city', 'district', 'address', 'website', 'contact_person'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input'}),
            'company_description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Şirketinizi tanıtın...'
            }),
            'company_size': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'district': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://...'
            }),
            'contact_person': forms.TextInput(attrs={'class': 'form-input'}),
        }


class PasswordChangeForm(forms.Form):
    """Şifre değiştirme formu"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mevcut şifre'
        }),
        label='Mevcut Şifre'
    )
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Yeni şifre'
        }),
        label='Yeni Şifre',
        min_length=8
    )
    
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Yeni şifre tekrar'
        }),
        label='Yeni Şifre Tekrar'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Mevcut şifre hatalı.')
        return old_password
    
    def clean_new_password_confirm(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_confirm = self.cleaned_data.get('new_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValidationError('Yeni şifreler eşleşmiyor.')
        
        return new_password_confirm
      
