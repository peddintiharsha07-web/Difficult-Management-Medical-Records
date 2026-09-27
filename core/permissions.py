from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'PATIENT')


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'DOCTOR')


class IsHospitalAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'HOSPITAL_ADMIN')


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'SYSTEM_ADMIN')


class IsDoctorOrHospitalAdminOrSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                     request.user.role in ('DOCTOR', 'HOSPITAL_ADMIN', 'SYSTEM_ADMIN'))


class IsOwnerPatientOrStaff(BasePermission):
    """Object-level: patients can only see their own data; staff roles can see all."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ('DOCTOR', 'HOSPITAL_ADMIN', 'SYSTEM_ADMIN'):
            return True
        patient = getattr(obj, 'patient', obj)
        return getattr(patient, 'user_id', None) == user.id
