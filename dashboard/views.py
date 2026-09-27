from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from appointments.models import Appointment
from medical_records.models import MedicalRecord
from users.models import User, AuditLog


@login_required
def home(request):
    user = request.user

    if user.role == User.Role.PATIENT:
        return patient_dashboard(request)
    elif user.role == User.Role.DOCTOR:
        return doctor_dashboard(request)
    elif user.role == User.Role.HOSPITAL_ADMIN:
        return hospital_dashboard(request)
    elif user.role == User.Role.SYSTEM_ADMIN:
        return system_admin_dashboard(request)
    return redirect('core:home')


def patient_dashboard(request):
    profile = getattr(request.user, 'patient_profile', None)
    if profile is None:
        return render(request, 'dashboard/patient_dashboard.html', {'profile': None})

    upcoming = profile.appointments.filter(
        appointment_date__gte=timezone.now().date()
    ).exclude(status__in=['CANCELLED', 'REJECTED']).order_by('appointment_date', 'appointment_time')[:5]
    records = profile.medical_records.all()[:5]

    context = {
        'profile': profile,
        'upcoming_appointments': upcoming,
        'total_appointments': profile.appointments.count(),
        'recent_records': records,
        'total_records': profile.medical_records.count(),
        'allergies': profile.allergies.all(),
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


def doctor_dashboard(request):
    profile = getattr(request.user, 'doctor_profile', None)
    if profile is None:
        return render(request, 'dashboard/doctor_incomplete.html')

    today = timezone.now().date()
    todays_appointments = profile.appointments.filter(appointment_date=today).order_by('appointment_time')
    pending_appointments = profile.appointments.filter(status='PENDING').order_by('appointment_date')
    recent_records = profile.medical_records.all()[:5]
    total_patients = profile.medical_records.values('patient').distinct().count()

    context = {
        'profile': profile,
        'todays_appointments': todays_appointments,
        'pending_appointments': pending_appointments,
        'recent_records': recent_records,
        'total_patients': total_patients,
    }
    return render(request, 'dashboard/doctor_dashboard.html', context)


def hospital_dashboard(request):
    hospital = getattr(request.user, 'hospital', None)
    if hospital is None:
        return render(request, 'dashboard/hospital_incomplete.html')

    today = timezone.now().date()
    context = {
        'hospital': hospital,
        'total_doctors': hospital.doctors.count(),
        'total_patients': MedicalRecord.objects.filter(hospital=hospital).values('patient').distinct().count(),
        'todays_appointments': hospital.appointments.filter(appointment_date=today).count(),
        'departments': hospital.departments.all(),
        'recent_appointments': hospital.appointments.order_by('-created_at')[:8],
        'pending_share_requests': hospital.share_requests.filter(status='PENDING'),
    }
    return render(request, 'dashboard/hospital_dashboard.html', context)


def system_admin_dashboard(request):
    from hospitals.models import Hospital
    from doctors.models import DoctorProfile
    from patients.models import PatientProfile

    context = {
        'total_hospitals': Hospital.objects.count(),
        'pending_hospitals': Hospital.objects.filter(status='PENDING').count(),
        'total_doctors': DoctorProfile.objects.count(),
        'pending_doctors': User.objects.filter(role='DOCTOR', status='PENDING').count(),
        'total_patients': PatientProfile.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'total_records': MedicalRecord.objects.count(),
        'recent_audit_logs': AuditLog.objects.all()[:15],
    }
    return render(request, 'dashboard/system_admin_dashboard.html', context)
