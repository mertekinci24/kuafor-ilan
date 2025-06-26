from django import forms
from .models import JobSeekerProfile, BusinessProfile

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'

class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = '__all__'
      
