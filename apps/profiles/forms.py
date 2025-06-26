from django import forms
from .models import JobSeekerProfile, BusinessProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            'bio', 'experience_years', 'skills', 
            'city', 'district', 'is_available'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Kendinizi tanıtın...'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Saç kesimi, boyama, makyaj...'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İstanbul'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kadıköy'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            'business_name', 'description', 'address', 
            'city', 'district', 'phone', 'website'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Salon Adınız'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Salonunuzu tanıtın...'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tam adresiniz'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İstanbul'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kadıköy'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0555 123 45 67'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        
