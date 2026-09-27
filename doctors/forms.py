from django import forms
from .models import DoctorProfile


class DoctorProfileCompletionForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['hospital', 'department', 'specialization', 'license_number',
                  'years_of_experience', 'consultation_fee', 'bio']
