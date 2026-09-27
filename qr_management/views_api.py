from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PatientQRCode
from .serializers import PatientQRCodeSerializer


class PatientQRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PatientQRCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = PatientQRCode.objects.select_related('patient__user')
        if user.role == 'PATIENT':
            return qs.filter(patient__user=user)
        return qs

    @action(detail=False, methods=['get'], url_path='verify/(?P<token>[^/.]+)')
    def verify(self, request, token=None):
        try:
            qr = PatientQRCode.objects.select_related('patient__user').get(token=token, is_active=True)
        except (PatientQRCode.DoesNotExist, ValueError):
            return Response({'detail': 'Invalid or inactive QR code.'}, status=404)
        return Response({
            'medical_id': qr.patient.medical_id,
            'patient_name': qr.patient.user.get_full_name(),
        })
