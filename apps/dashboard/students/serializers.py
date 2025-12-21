from apps.headless.students.models import Student
from rest_framework import serializers



class StudentListSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(read_only=True)
    enrollments_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model=Student
        fields=['uuid', 'identifier', 'enrollments_count', 'created_at']