from apps.core.constants import DefaultObjectKeys, ENV, Urls
from apps.core.utilities import S3Utils
from apps.dashboard.instructors.models import Instructor
from apps.headless.courses.models import Enrollments
from rest_framework import serializers

from .models import Course, CourseLesson, LessonResource



class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_null=True)
    thumbnail = serializers.CharField(required=True, write_only=True)
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    access_status = serializers.CharField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    thumbnail_url = serializers.SerializerMethodField(read_only=True)
    enrollments = serializers.IntegerField(read_only=True, source='enrollments_count')

    class Meta:
        model = Course
        fields = [
            'uuid', 'created_at', 'access_status', 'thumbnail_url', 'enrollments',
            'title', 'description', 'thumbnail', 'duration', 'created_by'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_thumbnail_url(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return Urls.STATIC_S3_URL + thumbnail


class CourseRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    access_status = serializers.CharField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    enrollments = serializers.IntegerField(read_only=True, source='enrollments_count')

    class Meta:
        model = Course
        fields = [
            'uuid', 'created_at', 'title', 'description',
            'duration', 'access_status', 'created_by', 'thumbnail_url',
            'enrollments'
        ]

    def get_thumbnail_url(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return Urls.STATIC_S3_URL + thumbnail
    

class CourseUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_null=True)
    thumbnail = serializers.CharField(required=False)
    access_status = serializers.BooleanField(required=True)

    class Meta:
        model = Course
        fields = [
            'uuid', 'created_at', 'access_status',
            'title', 'description', 'thumbnail'
        ]
        read_only_fields = ['uuid', 'created_at']


class CourseLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    access_status = serializers.CharField(read_only=True)
    media_key = serializers.CharField(required=False, default=None, write_only=True)
    media_size = serializers.IntegerField(read_only=True)
    course_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'created_at', 'title', 'access_status',
            'description', 'duration', 'media_key', 'media_size',
            'course_uuid'
        ]
        read_only_fields = ['uuid', 'created_at']


class CourseLessonRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    access_status = serializers.CharField(read_only=True)
    media_size = serializers.IntegerField(read_only=True)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'created_at', 'title', 'access_status',
            'description', 'duration', 'video_url', 'media_size'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_video_url(self, obj):
        video_key = obj.media_key
        if not video_key:
            return None
        return S3Utils.get_signed_url(video_key)
    

class CourseLessonUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    access_status = serializers.BooleanField(required=False)

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'created_at', 'title', 'description', 'access_status',
        ]
        read_only_fields = ['uuid', 'created_at']


class LessonResourceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    file_name = serializers.CharField(required=True)
    file_size = serializers.IntegerField(required=True)
    file_type = serializers.CharField(required=True)
    file_key = serializers.CharField(required=True)
    notes = serializers.CharField(required=False)
    related_links = serializers.JSONField(required=False)
    lesson_uuid = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = LessonResource
        fields = [
            'uuid', 'created_at', 'title', 'file_name', 
            'file_size', 'file_type', 'file_key', 'notes',
            'related_links', 'lesson_uuid',
        ]
        read_only_fields = ['uuid', 'created_at']


class LessonTextResourceSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False)
    related_links = serializers.JSONField(required=False)
    lesson_uuid = serializers.UUIDField(required=True, write_only=True)

    class Meta:
        model = LessonResource
        fields = [
            'uuid', 'created_at', 'notes',
            'related_links', 'lesson_uuid',
        ]
        read_only_fields = ['uuid', 'created_at']

    def validate_related_links(self, value):
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("Related links must be a array of objects.")
            for item in value:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("Each item in the related links array must be an object.")
                if not item.get('title') or not item.get('url'):
                    raise serializers.ValidationError("Each item in the related links array must have a title and url.")
            
        return value
        

class EnrollmentsListSerializer(serializers.ModelSerializer):
    course_uuid = serializers.UUIDField(source='course.uuid')
    student_uuid = serializers.UUIDField(source='student.uuid')
    course_title = serializers.CharField(source='course.title')
    student_identifier = serializers.CharField(source='student.identifier')
    enrolled_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model=Enrollments
        fields = ['uuid', 'course_uuid', 'student_uuid', 
                  'course_title', 'student_identifier', 'enrolled_at']