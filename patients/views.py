from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import PatientProfile, Allergy, Vaccination
from appointments.models import Appointment
from doctors.models import DoctorProfile


def _require_patient(request):
    if request.user.role != 'PATIENT':
        raise PermissionDenied("Only patients can access this page.")


@login_required
def my_records(request):
    _require_patient(request)
    profile = request.user.patient_profile
    records = profile.medical_records.select_related('doctor__user', 'hospital').prefetch_related(
        'prescriptions', 'lab_reports', 'attachments')
    return render(request, 'patients/my_records.html', {'records': records, 'profile': profile})


@login_required
def record_detail(request, record_id):
    _require_patient(request)
    profile = request.user.patient_profile
    record = get_object_or_404(profile.medical_records.select_related('doctor__user', 'hospital'), id=record_id)
    return render(request, 'patients/record_detail.html', {'record': record})


@login_required
def my_qr_card(request):
    _require_patient(request)
    profile = request.user.patient_profile
    return render(request, 'patients/qr_card.html', {'profile': profile})


@login_required
def edit_profile(request):
    _require_patient(request)
    profile = request.user.patient_profile
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.save()

        profile.gender = request.POST.get('gender', profile.gender)
        profile.blood_group = request.POST.get('blood_group', profile.blood_group)
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.chronic_diseases = request.POST.get('chronic_diseases', '')
        profile.current_medications = request.POST.get('current_medications', '')
        profile.organ_donor = request.POST.get('organ_donor') == 'on'
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('patients:edit_profile')
    return render(request, 'patients/edit_profile.html', {'profile': profile})


@login_required
def book_appointment(request):
    _require_patient(request)
    profile = request.user.patient_profile
    doctors = DoctorProfile.objects.select_related('user', 'hospital').filter(user__status='APPROVED')

    if request.method == 'POST':
        doctor = get_object_or_404(DoctorProfile, id=request.POST.get('doctor'))
        Appointment.objects.create(
            patient=profile,
            doctor=doctor,
            hospital=doctor.hospital,
            appointment_date=request.POST.get('appointment_date'),
            appointment_time=request.POST.get('appointment_time'),
            reason=request.POST.get('reason', ''),
        )
        messages.success(request, 'Appointment requested. You will be notified once the doctor responds.')
        return redirect('patients:my_appointments')

    return render(request, 'patients/book_appointment.html', {'doctors': doctors})


@login_required
def my_appointments(request):
    _require_patient(request)
    profile = request.user.patient_profile
    appts = profile.appointments.select_related('doctor__user', 'hospital').all()
    return render(request, 'patients/my_appointments.html', {'appointments': appts})


@login_required
def cancel_appointment(request, appointment_id):
    _require_patient(request)
    profile = request.user.patient_profile
    appt = get_object_or_404(Appointment, id=appointment_id, patient=profile)
    appt.status = 'CANCELLED'
    appt.save(update_fields=['status'])
    messages.info(request, 'Appointment cancelled.')
    return redirect('patients:my_appointments')
