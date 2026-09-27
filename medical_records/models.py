import uuid
from django.db import models


class MedicalRecord(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        CLOSED = 'CLOSED', 'Closed'
        DISCHARGED = 'DISCHARGED', 'Discharged'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.SET_NULL, null=True,
                                related_name='medical_records')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, null=True,
                                  related_name='medical_records')
    consultation_date = models.DateTimeField()
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_details = models.TextField(blank=True)
    follow_up_notes = models.TextField(blank=True)
    discharge_summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-consultation_date']

    def __str__(self):
        return f"Record {self.id} - {self.patient.medical_id}"


class Prescription(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medication_name} - {self.record.patient.medical_id}"


class LabReport(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_reports')
    title = models.CharField(max_length=200)
    report_date = models.DateField()
    file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.record.patient.medical_id}"


class MedicalAttachment(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description or str(self.file)
