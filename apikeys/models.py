from core.models import TimeStampedModel, SoftDeleteMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from instructors.models import Instructor



class ApiKeyTypes(models.TextChoices):
    PUBLIC = 'public', _('Public')
    PRIVATE = 'private', _('Private')


class ApiKeys(TimeStampedModel, SoftDeleteMixin):
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name="apikeys")
    key_name = models.CharField(max_length=255)
    key_hash = models.CharField(max_length=128)
    key_type = models.CharField(max_length=50, choices=ApiKeyTypes.choices, default=ApiKeyTypes.PUBLIC)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['instructor', 'key_name', 'key_type']
        managed=True
        db_table="instructors_apikeys"
        ordering = ["-created_at"]
