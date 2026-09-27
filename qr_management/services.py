import io
import qrcode
from django.core.files.base import ContentFile
from .models import PatientQRCode


def generate_qr_for_patient(patient_profile):
    """
    Create (or refresh) a QR code for a patient. The QR encodes a URL that
    doctors/hospitals can scan to hit the secure lookup endpoint using the
    signed token - never the raw medical ID or personal data.
    """
    qr_obj, _ = PatientQRCode.objects.get_or_create(patient=patient_profile)

    payload = f"MEDRECORD:{qr_obj.token}"
    img = qrcode.make(payload, box_size=10, border=2)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    filename = f"qr_{patient_profile.medical_id}.png"
    qr_obj.image.save(filename, ContentFile(buffer.getvalue()), save=True)
    return qr_obj
