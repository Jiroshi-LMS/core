from django.db import models
from core.models import TimeStampedModel, SoftDeleteMixin
from instructors.models import Instructor
from simple_history.models import HistoricalRecords



class Course(TimeStampedModel, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(
        Instructor, on_delete=models.DO_NOTHING, related_name='lessons'
    )
    
    history = HistoricalRecords()

    class Meta:
        db_table = 'course_lessons'
        verbose_name_plural = 'Course Lessons'
        ordering = ['-created_at']