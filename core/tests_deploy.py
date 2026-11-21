"""Vercel-friendly storage + optional open doctor access."""
from django.test import override_settings
from django.urls import reverse

from core.storage import DatabaseStorage
from core.testing import BaseTestCase, pdf_file

DB_STORAGES = {
    'default': {'BACKEND': 'core.storage.DatabaseStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


@override_settings(STORAGES=DB_STORAGES)
class DatabaseStorageFlowTests(BaseTestCase):
    """Upload -> stored in the DB (no disk) -> owner can still download it."""

    def setUp(self):
        self.pat, self.profile = self.make_patient('owner')
        self.login(self.pat)
        self.client.post(reverse('medical_records:document_upload'), {
            'category': 'LAB_REPORT', 'title': 'Blood test', 'record_date': '2025-01-10',
            'file': pdf_file(), 'shared_with_doctors': 'on'})

    def test_file_lives_in_database_not_on_disk(self):
        from core.models import StoredFile
        doc = self.profile.documents.get()
        self.assertEqual(StoredFile.objects.filter(name=doc.file.name).count(), 1)
        self.assertTrue(StoredFile.objects.get(name=doc.file.name).content.startswith(b'%PDF'))

    def test_owner_can_download_from_db_storage(self):
        doc = self.profile.documents.get()
        r = self.client.get(reverse('medical_records:file', args=['document', doc.pk]))
        self.assertEqual((r.status_code, r['Content-Type']), (200, 'application/pdf'))
        self.assertTrue(b''.join(r.streaming_content).startswith(b'%PDF'))

    def test_delete_removes_stored_bytes(self):
        from core.models import StoredFile
        doc = self.profile.documents.get()
        name = doc.file.name
        DatabaseStorage().delete(name)
        self.assertFalse(StoredFile.objects.filter(name=name).exists())

    def test_url_is_never_public(self):
        with self.assertRaises(NotImplementedError):
            DatabaseStorage().url('x')


class DoctorOpenAccessTests(BaseTestCase):
    def setUp(self):
        self.pat, self.profile = self.make_patient('asha')
        self.doc_user, self.doc = self.make_doctor('drx')
        self.login(self.pat)
        self.client.post(reverse('medical_records:document_upload'), {
            'category': 'LAB_REPORT', 'title': 'Shared one', 'record_date': '2025-01-10',
            'file': pdf_file(), 'shared_with_doctors': 'on'})
        self.client.post(reverse('medical_records:document_upload'), {
            'category': 'LAB_REPORT', 'title': 'Private one', 'record_date': '2025-01-10',
            'file': pdf_file()})
        self.url = reverse('doctors:patient_detail', args=[self.profile.medical_id])
        self.login(self.doc_user)

    def test_default_is_consent_only(self):
        self.assertEqual(self.client.get(self.url).status_code, 403)

    @override_settings(DOCTOR_OPEN_ACCESS=True)
    def test_open_access_shows_patient_to_any_approved_doctor(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Shared one')
        self.assertNotContains(r, 'Private one')          # patient's private switch still respected

    @override_settings(DOCTOR_OPEN_ACCESS=True)
    def test_open_access_is_read_only_and_logged(self):
        from consents.models import RecordAccessLog
        self.client.get(self.url)
        self.assertTrue(RecordAccessLog.objects.filter(patient=self.profile).exists())  # patient can see it
        self.assertEqual(self.client.get(reverse('doctors:create_record', args=[self.profile.medical_id]),
                                         follow=False).status_code, 302)  # no consultation notes

    @override_settings(DOCTOR_OPEN_ACCESS=True)
    def test_unapproved_doctor_and_other_roles_still_blocked(self):
        pending, _ = self.make_doctor('pend', status='PENDING')
        self.login(pending)
        self.assertNotEqual(self.client.get(self.url).status_code, 200)
        self.login(self.make_hospital_admin())
        self.assertNotEqual(self.client.get(self.url).status_code, 200)
