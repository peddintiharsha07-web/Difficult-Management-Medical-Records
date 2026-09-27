import uuid
from django.db import models


class PatientQRCode(models.Model):
    """
    A secure QR code tied to a patient's Medical ID.
    The QR encodes a signed token (not the raw medical ID) so it can be
    verified server-side and rotated if compromised.
    """
    patient = models.OneToOneField('patients.PatientProfile', on_delete=models.CASCADE, related_name='qr_code')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"QR for {self.patient.medical_id}"
