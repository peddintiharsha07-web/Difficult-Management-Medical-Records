from rest_framework import viewsets, permissions
from .models import MedicalRecord, Prescription, LabReport, MedicalAttachment
from .serializers import (MedicalRecordSerializer, PrescriptionSerializer,
                           LabReportSerializer, MedicalAttachmentSerializer)


class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = MedicalRecord.objects.select_related('patient__user', 'doctor__user', 'hospital')
        if user.role == 'PATIENT':
            return qs.filter(patient__user=user)
        if user.role == 'DOCTOR':
            return qs.filter(doctor__user=user)
        if user.role == 'HOSPITAL_ADMIN':
            return qs.filter(hospital__admin=user)
        return qs


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]


class LabReportViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = LabReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class MedicalAttachmentViewSet(viewsets.ModelViewSet):
    queryset = MedicalAttachment.objects.all()
    serializer_class = MedicalAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
