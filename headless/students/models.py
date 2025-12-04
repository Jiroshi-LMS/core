from django.db import models
from core.models import TimeStampedModel, SoftDeleteMixin
from instructors.models import Instructor


class Student(TimeStampedModel, SoftDeleteMixin):
    identifier = models.CharField(max_length=255)
    password = models.CharField(max_length=72)
    instructor = models.ForeignKey(Instructor, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "students"
        verbose_name_plural = 'Students'
        ordering = ['-created_at']
        unique_together = (('identifier', 'instructor'),)

    @property
    def owner_field(self):
        return "created_by"