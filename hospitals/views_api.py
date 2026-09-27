from rest_framework import viewsets, permissions
from .models import Hospital, Department, HospitalStaff, RecordShareRequest
from .serializers import (HospitalSerializer, DepartmentSerializer,
                           HospitalStaffSerializer, RecordShareRequestSerializer)


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class HospitalStaffViewSet(viewsets.ModelViewSet):
    queryset = HospitalStaff.objects.all()
    serializer_class = HospitalStaffSerializer
    permission_classes = [permissions.IsAuthenticated]


class RecordShareRequestViewSet(viewsets.ModelViewSet):
    queryset = RecordShareRequest.objects.all()
    serializer_class = RecordShareRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
