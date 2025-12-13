from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteMixin
from apps.headless.students.models import Student
from apps.dashboard.courses.models import Course


class Enrollments(TimeStampedModel, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course")

    class Meta:
        managed=True
        db_table = 'course_enrollments'
        unique_together=['student', 'course']