from rest_framework import viewsets, permissions
from .models import PatientProfile, Allergy, Vaccination
from .serializers import PatientProfileSerializer, AllergySerializer, VaccinationSerializer
from core.permissions import IsDoctorOrHospitalAdminOrSystemAdmin


class PatientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return PatientProfile.objects.filter(user=user)
        return PatientProfile.objects.all()


class AllergyViewSet(viewsets.ModelViewSet):
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Allergy.objects.filter(patient__user=user)
        return Allergy.objects.all()


class VaccinationViewSet(viewsets.ModelViewSet):
    serializer_class = VaccinationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Vaccination.objects.filter(patient__user=user)
        return Vaccination.objects.all()
