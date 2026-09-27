from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import Hospital, Department, HospitalStaff, RecordShareRequest
from .forms import HospitalProfileForm, DepartmentForm
from doctors.models import DoctorProfile
from users.models import AuditLog


def _require_hospital_admin(request):
    if request.user.role != 'HOSPITAL_ADMIN':
        raise PermissionDenied("Only hospital administrators can access this page.")


@login_required
def complete_profile(request):
    _require_hospital_admin(request)
    if hasattr(request.user, 'hospital'):
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = HospitalProfileForm(request.POST, request.FILES)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.admin = request.user
            hospital.save()
            messages.success(request, 'Hospital profile submitted for system administrator approval.')
            return redirect('dashboard:home')
    else:
        form = HospitalProfileForm()
    return render(request, 'hospitals/complete_profile.html', {'form': form})


@login_required
def manage_departments(request):
    _require_hospital_admin(request)
    hospital = request.user.hospital
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save(commit=False)
            dept.hospital = hospital
            dept.save()
            messages.success(request, 'Department added.')
            return redirect('hospitals:manage_departments')
    else:
        form = DepartmentForm()
    return render(request, 'hospitals/manage_departments.html', {
        'hospital': hospital, 'departments': hospital.departments.all(), 'form': form})


@login_required
def manage_doctors(request):
    _require_hospital_admin(request)
    hospital = request.user.hospital
    doctors = DoctorProfile.objects.filter(hospital=hospital).select_related('user', 'department')
    return render(request, 'hospitals/manage_doctors.html', {'hospital': hospital, 'doctors': doctors})


@login_required
def manage_staff(request):
    _require_hospital_admin(request)
    hospital = request.user.hospital
    if request.method == 'POST':
        HospitalStaff.objects.create(
            hospital=hospital,
            full_name=request.POST.get('full_name'),
            role_title=request.POST.get('role_title'),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
        )
        messages.success(request, 'Staff member added.')
        return redirect('hospitals:manage_staff')
    return render(request, 'hospitals/manage_staff.html', {
        'hospital': hospital, 'staff': hospital.staff.all()})


@login_required
def manage_appointments(request):
    _require_hospital_admin(request)
    hospital = request.user.hospital
    appointments = hospital.appointments.select_related('patient__user', 'doctor__user').all()
    return render(request, 'hospitals/manage_appointments.html', {'appointments': appointments})


@login_required
def share_requests(request):
    _require_hospital_admin(request)
    hospital = request.user.hospital
    requests_qs = hospital.share_requests.select_related('patient__user').all()
    return render(request, 'hospitals/share_requests.html', {'requests': requests_qs})


@login_required
def request_record_access(request):
    """Hospital admin requests access to a patient's shared record by Medical ID."""
    _require_hospital_admin(request)
    hospital = request.user.hospital
    if request.method == 'POST':
        from patients.models import PatientProfile
        medical_id = request.POST.get('medical_id', '').upper()
        try:
            patient = PatientProfile.objects.get(medical_id=medical_id)
            RecordShareRequest.objects.get_or_create(
                hospital=hospital, patient=patient,
                defaults={'reason': request.POST.get('reason', '')})
            messages.success(request, f'Access request sent for patient {medical_id}.')
        except PatientProfile.DoesNotExist:
            messages.error(request, 'No patient found with that Medical ID.')
    return redirect('hospitals:share_requests')
