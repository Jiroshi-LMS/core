from core.models import TimeStampedModel, SoftDeleteMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from instructors.models import Instructor
from simple_history.models import HistoricalRecords



class Course(TimeStampedModel, SoftDeleteMixin):

    ACCESS_STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('draft', _('Draft')),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField(default=0)
    access_status = models.CharField(max_length=20, choices=ACCESS_STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        Instructor, on_delete=models.DO_NOTHING, related_name='courses'
    )
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'courses'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        unique_together = ('title', 'created_by')
        

class CourseLesson(TimeStampedModel, SoftDeleteMixin):

    ACCESS_STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('draft', _('Draft')),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField(default=0)
    access_status = models.CharField(max_length=20, choices=ACCESS_STATUS_CHOICES, default='draft')
    media_key = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        Instructor, on_delete=models.DO_NOTHING, related_name='lessons'
    )
    
    history = HistoricalRecords()

    class Meta:
        db_table = 'course_lessons'
        verbose_name_plural = 'Course Lessons'
        ordering = ['-created_at']