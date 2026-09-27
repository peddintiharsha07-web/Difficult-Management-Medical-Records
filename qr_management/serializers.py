from rest_framework import serializers
from .models import PatientQRCode


class PatientQRCodeSerializer(serializers.ModelSerializer):
    medical_id = serializers.CharField(source='patient.medical_id', read_only=True)

    class Meta:
        model = PatientQRCode
        fields = ['id', 'patient', 'medical_id', 'token', 'image', 'is_active', 'created_at', 'rotated_at']
        read_only_fields = ['id', 'token', 'created_at', 'rotated_at']
