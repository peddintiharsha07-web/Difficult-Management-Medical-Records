"""Database-backed file storage for hosts without a persistent disk (e.g. Vercel serverless).

Files are stored as rows of ``core.StoredFile``. They are private: ``url()`` is deliberately
unsupported, so a file can only be streamed by a permission-checked view (see
``medical_records.files.serve_file``), exactly like the filesystem/S3 setups.
"""
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseStorage(Storage):
    def _model(self):
        from core.models import StoredFile  # imported lazily: storage is loaded before apps are ready
        return StoredFile

    def _open(self, name, mode='rb'):
        try:
            row = self._model().objects.only('content').get(name=name)
        except self._model().DoesNotExist:
            raise FileNotFoundError(name)
        return ContentFile(bytes(row.content), name=name)

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        if isinstance(data, str):
            data = data.encode()
        self._model().objects.update_or_create(name=name, defaults={'content': data, 'size': len(data)})
        return name

    def exists(self, name):
        return self._model().objects.filter(name=name).exists()

    def delete(self, name):
        self._model().objects.filter(name=name).delete()

    def size(self, name):
        try:
            return self._model().objects.values_list('size', flat=True).get(name=name)
        except self._model().DoesNotExist:
            raise FileNotFoundError(name)

    def url(self, name):
        raise NotImplementedError('Files are private and are only served through permission-checked views.')

    def get_available_name(self, name, max_length=None):
        return super().get_available_name(name.replace('\\', '/'), max_length)
