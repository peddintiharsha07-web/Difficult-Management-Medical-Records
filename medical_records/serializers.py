from rest_framework import serializers
from .models import MedicalRecord, Prescription, LabReport, MedicalAttachment


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'record', 'medication_name', 'dosage', 'frequency', 'duration',
                  'notes', 'file', 'created_at']


class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = ['id', 'record', 'title', 'report_date', 'file', 'notes', 'uploaded_at']


class MedicalAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalAttachment
        fields = ['id', 'record', 'file', 'description', 'uploaded_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_medical_id = serializers.CharField(source='patient.medical_id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    lab_reports = LabReportSerializer(many=True, read_only=True)
    attachments = MedicalAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'patient_medical_id', 'doctor', 'doctor_name', 'hospital',
                  'hospital_name', 'consultation_date', 'symptoms', 'diagnosis',
                  'treatment_details', 'follow_up_notes', 'discharge_summary', 'status',
                  'prescriptions', 'lab_reports', 'attachments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
