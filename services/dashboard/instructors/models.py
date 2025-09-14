from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel, SoftDeleteMixin


class Instructor(AbstractUser, TimeStampedModel, SoftDeleteMixin):
    full_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    class Meta:
        db_table = 'instructors'
        verbose_name_plural = 'Instructors'

    def __str__(self):
        return self.username