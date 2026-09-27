from rest_framework import serializers
from .models import Hospital, Department, HospitalStaff, RecordShareRequest


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'hospital', 'name', 'description']


class HospitalSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = ['id', 'admin', 'name', 'registration_number', 'address', 'city', 'state',
                  'phone', 'email', 'logo', 'status', 'departments', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class HospitalStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalStaff
        fields = ['id', 'hospital', 'full_name', 'role_title', 'phone', 'email', 'is_active']


class RecordShareRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordShareRequest
        fields = ['id', 'hospital', 'patient', 'status', 'requested_at', 'decided_at', 'reason']
        read_only_fields = ['id', 'requested_at', 'decided_at']
