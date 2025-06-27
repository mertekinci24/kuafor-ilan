from django import forms
from .models import JobSeekerProfile, BusinessProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            'bio', 'experience_years', 'skills', 
            'city', 'district', 'is_available', 'birth_date', 'address',
            'portfolio_url', 'linkedin_url', 'cv_file', 'profile_image',
            'certificates', 'expected_salary_min', 'expected_salary_max'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Kendinizi tanıtın...'}),
            'experience_years': forms.Select(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Saç kesimi, boyama, makyaj...'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İstanbul'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kadıköy'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tam adresiniz'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'expected_salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opsiyonel'}),
            'expected_salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opsiyonel'}),
        }
        
class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'company_name', 'company_description', 'address', 
            'city', 'district', 'contact_phone', 'website',
            'company_size', 'establishment_year', 'contact_person',
            'is_verified', 'verification_documents', 'logo', 'cover_image'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salon Adınız'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Salonunuzu tanıtın...'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tam adresiniz'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İstanbul'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kadıköy'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0555 123 45 67'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'establishment_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Opsiyonel'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İletişim kurulacak kişi'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

