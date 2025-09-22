from rest_framework import serializers
from .models import Course, CourseLesson
from instructors.models import Instructor


class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    thumbnail = serializers.CharField(required=False, default=None)
    duration = serializers.DecimalField(required=False, default=None, max_digits=5, decimal_places=2)
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            'uuid', 'created_at',
            'title', 'description', 'thumbnail', 'duration', 'created_by'
        ]
        read_only_fields = ['uuid', 'created_at']