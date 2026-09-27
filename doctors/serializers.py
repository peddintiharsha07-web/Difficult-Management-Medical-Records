from rest_framework import serializers
from .models import DoctorProfile


class DoctorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'full_name', 'hospital', 'hospital_name', 'department',
                  'specialization', 'license_number', 'years_of_experience',
                  'consultation_fee', 'bio', 'is_emergency_authorized', 'created_at']
        read_only_fields = ['id', 'created_at']
