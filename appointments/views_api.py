from rest_framework import viewsets, permissions
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related('patient__user', 'doctor__user', 'hospital')
        if user.role == 'PATIENT':
            return qs.filter(patient__user=user)
        if user.role == 'DOCTOR':
            return qs.filter(doctor__user=user)
        if user.role == 'HOSPITAL_ADMIN':
            return qs.filter(hospital__admin=user)
        return qs
