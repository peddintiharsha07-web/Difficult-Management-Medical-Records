from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import DoctorProfile
from .forms import DoctorProfileCompletionForm
from patients.models import PatientProfile
from qr_management.models import PatientQRCode
from medical_records.models import MedicalRecord, Prescription, LabReport
from appointments.models import Appointment
from users.models import AuditLog


def _require_doctor(request):
    if request.user.role != 'DOCTOR':
        raise PermissionDenied("Only doctors can access this page.")


@login_required
def complete_profile(request):
    _require_doctor(request)
    if hasattr(request.user, 'doctor_profile'):
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = DoctorProfileCompletionForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile completed.')
            return redirect('dashboard:home')
    else:
        form = DoctorProfileCompletionForm()
    return render(request, 'doctors/complete_profile.html', {'form': form})


@login_required
def search_patient(request):
    _require_doctor(request)
    query = request.GET.get('q', '').strip()
    patient = None
    error = None
    if query:
        try:
            patient = PatientProfile.objects.select_related('user').get(medical_id=query.upper())
        except PatientProfile.DoesNotExist:
            error = 'No patient found with that Medical ID.'
    return render(request, 'doctors/search_patient.html', {'query': query, 'patient': patient, 'error': error})


@login_required
def scan_qr(request):
    """Handles lookup after a QR scan: token is embedded as MEDRECORD:<uuid>."""
    _require_doctor(request)
    token = request.GET.get('token', '').replace('MEDRECORD:', '').strip()
    patient = None
    error = None
    if token:
        try:
            qr = PatientQRCode.objects.select_related('patient__user').get(token=token, is_active=True)
            patient = qr.patient
        except (PatientQRCode.DoesNotExist, ValueError):
            error = 'Invalid or inactive QR code.'
    return render(request, 'doctors/scan_qr.html', {'patient': patient, 'error': error, 'token': token})


@login_required
def patient_detail(request, medical_id):
    _require_doctor(request)
    patient = get_object_or_404(PatientProfile.objects.select_related('user'), medical_id=medical_id)
    records = patient.medical_records.select_related('doctor__user', 'hospital').all()
    AuditLog.objects.create(actor=request.user, action_type=AuditLog.ActionType.RECORD_VIEW,
                             description=f'Dr. {request.user.get_full_name()} viewed records for {medical_id}',
                             target_object=medical_id)
    return render(request, 'doctors/patient_detail.html', {'patient': patient, 'records': records})


@login_required
def create_record(request, medical_id):
    _require_doctor(request)
    patient = get_object_or_404(PatientProfile, medical_id=medical_id)
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if doctor_profile is None:
        messages.error(request, 'Complete your doctor profile first.')
        return redirect('doctors:complete_profile')

    if request.method == 'POST':
        record = MedicalRecord.objects.create(
            patient=patient,
            doctor=doctor_profile,
            hospital=doctor_profile.hospital,
            consultation_date=request.POST.get('consultation_date'),
            symptoms=request.POST.get('symptoms', ''),
            diagnosis=request.POST.get('diagnosis', ''),
            treatment_details=request.POST.get('treatment_details', ''),
            follow_up_notes=request.POST.get('follow_up_notes', ''),
            discharge_summary=request.POST.get('discharge_summary', ''),
            status=request.POST.get('status', 'ACTIVE'),
        )

        med_names = request.POST.getlist('medication_name')
        dosages = request.POST.getlist('dosage')
        frequencies = request.POST.getlist('frequency')
        for name, dosage, freq in zip(med_names, dosages, frequencies):
            if name.strip():
                Prescription.objects.create(record=record, medication_name=name, dosage=dosage, frequency=freq)

        AuditLog.objects.create(actor=request.user, action_type=AuditLog.ActionType.RECORD_CREATE,
                                 description=f'Created medical record for {medical_id}',
                                 target_object=str(record.id))
        messages.success(request, 'Medical record created successfully.')
        return redirect('doctors:patient_detail', medical_id=medical_id)

    return render(request, 'doctors/create_record.html', {'patient': patient})


@login_required
def my_appointments(request):
    _require_doctor(request)
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    appts = doctor_profile.appointments.select_related('patient__user').all() if doctor_profile else []
    return render(request, 'doctors/my_appointments.html', {'appointments': appts})


@login_required
def update_appointment_status(request, appointment_id):
    _require_doctor(request)
    appt = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(Appointment.Status.choices):
        appt.status = new_status
        appt.save(update_fields=['status'])
        messages.success(request, f'Appointment marked as {appt.get_status_display()}.')
    return redirect('doctors:my_appointments')
