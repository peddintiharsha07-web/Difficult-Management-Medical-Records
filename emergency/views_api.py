from rest_framework import viewsets, permissions
from .models import EmergencyAccessLog
from .serializers import EmergencyAccessLogSerializer


class EmergencyAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmergencyAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = EmergencyAccessLog.objects.select_related('patient__user', 'accessed_by__user')
        if user.role == 'PATIENT':
            return qs.filter(patient__user=user)
        if user.role == 'DOCTOR':
            return qs.filter(accessed_by__user=user)
        return qs
