from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'address',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        user.status = User.Status.APPROVED

        if commit:
            user.save()

        return user


class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    mbbs_certificate = forms.FileField(
        required=True,
        label="MBBS Certificate",
        widget=forms.ClearableFileInput(
            attrs={
                'accept': '.pdf,.jpg,.jpeg,.png'
            }
        )
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'mbbs_certificate',
            'password1',
            'password2'
        )

    def clean_mbbs_certificate(self):
        file = self.cleaned_data.get('mbbs_certificate')

        if not file:
            raise forms.ValidationError(
                "Please upload your MBBS certificate."
            )

        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]

        if file.content_type not in allowed_types:
            raise forms.ValidationError(
                "Only PDF, JPG, JPEG or PNG files are allowed."
            )

        # 5 MB limit
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Certificate file must be less than 5 MB."
            )

        return file

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = User.Role.DOCTOR
        user.status = User.Status.PENDING

        if commit:
            user.save()

        return user


class HospitalAdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password1',
            'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = User.Role.HOSPITAL_ADMIN
        user.status = User.Status.PENDING

        if commit:
            user.save()

        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )