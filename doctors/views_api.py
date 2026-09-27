from rest_framework import viewsets, permissions
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer


class DoctorProfileViewSet(viewsets.ModelViewSet):
    queryset = DoctorProfile.objects.select_related('user', 'hospital', 'department').all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
