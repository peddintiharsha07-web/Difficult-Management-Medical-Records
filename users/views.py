from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import PatientRegistrationForm, DoctorRegistrationForm, HospitalAdminRegistrationForm
from .models import AuditLog
from patients.models import PatientProfile


def register_choice(request):
    return render(request, 'users/register_choice.html')


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PatientProfile.objects.create(user=user)
            login(request, user)
            AuditLog.objects.create(actor=user, action_type=AuditLog.ActionType.LOGIN,
                                     description='Patient registered and logged in')
            messages.success(request, 'Welcome! Your Medical ID and QR code have been generated.')
            return redirect('dashboard:home')
    else:
        form = PatientRegistrationForm()
    return render(request, 'users/register_patient.html', {'form': form})


def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration submitted. A system administrator must approve your '
                                       'account before you can log in.')
            return redirect('users:login')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'users/register_doctor.html', {'form': form})


def register_hospital(request):
    if request.method == 'POST':
        form = HospitalAdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration submitted. A system administrator must approve your '
                                       'hospital before you can log in.')
            return redirect('users:login')
    else:
        form = HospitalAdminRegistrationForm()
    return render(request, 'users/register_hospital.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'users/login.html')
        if user.role in ('DOCTOR', 'HOSPITAL_ADMIN') and user.status != 'APPROVED':
            messages.error(request, 'Your account is pending approval by a system administrator.')
            return render(request, 'users/login.html')
        if user.status == 'SUSPENDED':
            messages.error(request, 'Your account has been suspended. Contact support.')
            return render(request, 'users/login.html')
        login(request, user)
        AuditLog.objects.create(actor=user, action_type=AuditLog.ActionType.LOGIN,
                                 description=f'{user.username} logged in',
                                 ip_address=request.META.get('REMOTE_ADDR'))
        return redirect('dashboard:home')
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    AuditLog.objects.create(actor=request.user, action_type=AuditLog.ActionType.LOGOUT,
                             description=f'{request.user.username} logged out')
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user_obj': request.user})


def set_language_preference(request):
    if request.method == 'POST':
        lang = request.POST.get('language', 'en')
        request.session['django_language'] = lang
        if request.user.is_authenticated:
            request.user.preferred_language = lang
            request.user.save(update_fields=['preferred_language'])
    return redirect(request.META.get('HTTP_REFERER', '/'))
