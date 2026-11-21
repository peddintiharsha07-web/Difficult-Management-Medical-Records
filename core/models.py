from django.db import models
from django.utils import timezone


class ThrottleEvent(models.Model):
    """One row per *failed* attempt (bad login, bad QR token ...). Stored in the DB so the
    limit is shared by every worker and needs nothing beyond ``migrate``. ``key`` is a hash."""
    scope = models.CharField(max_length=32)
    key = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=['scope', 'key', 'created_at'])]


class StoredFile(models.Model):
    """File bytes kept in the database (see core.storage.DatabaseStorage). Used on hosts with no
    writable disk (Vercel) when no S3/R2 bucket is configured. Never exposed by URL."""
    name = models.CharField(max_length=255, unique=True)
    content = models.BinaryField()
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
