from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from .models import EmergencyAccessLog
from patients.models import PatientProfile
from qr_management.models import PatientQRCode


@login_required
def emergency_access(request):
    """One-click emergency access: doctor scans/enters a QR token and sees
    only critical information (blood group, allergies, medications, etc.)."""
    if request.user.role != 'DOCTOR':
        raise PermissionDenied("Only authorized doctors can use emergency access mode.")

    doctor_profile = getattr(request.user, 'doctor_profile', None)
    patient = None
    critical_info = None
    error = None

    if request.method == 'POST':
        token = request.POST.get('token', '').replace('MEDRECORD:', '').strip()
        reason = request.POST.get('reason', 'Emergency access')
        try:
            qr = PatientQRCode.objects.select_related('patient__user').get(token=token, is_active=True)
            patient = qr.patient
            critical_info = patient.critical_info

            EmergencyAccessLog.objects.create(
                patient=patient, accessed_by=doctor_profile, reason=reason,
                ip_address=request.META.get('REMOTE_ADDR'), patient_notified=True,
            )
            messages.warning(request, f'Emergency access to {patient.medical_id} has been logged '
                                       f'and the patient has been notified.')
        except (PatientQRCode.DoesNotExist, ValueError):
            error = 'Invalid or inactive QR code / token.'

    return render(request, 'emergency/access.html', {
        'patient': patient, 'critical_info': critical_info, 'error': error,
    })


@login_required
def my_emergency_logs(request):
    """Patients can see when their emergency info was accessed."""
    if request.user.role != 'PATIENT':
        raise PermissionDenied
    profile = request.user.patient_profile
    logs = profile.emergency_access_logs.select_related('accessed_by__user').all()
    return render(request, 'emergency/my_logs.html', {'logs': logs})
