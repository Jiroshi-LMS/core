from rest_framework import serializers
from apps.core.constants import DefaultObjectKeys, Urls, Units
from apps.core.utilities import S3Utils
from apps.dashboard.courses.models import Course, CourseLesson, LessonResource
from apps.headless.common.utilities.DynamicSerializerSelector import DynamicFieldsMixin

from .models import Enrollments


class CourseCatalogueSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    required_fields = ['is_enrolled']

    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    thumbnail = serializers.SerializerMethodField(read_only=True)
    duration = serializers.DecimalField(max_digits=10, decimal_places=4, required=True)
    is_enrolled = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model=Course
        fields = [
            'uuid', 'title', 'description',
            'thumbnail', 'duration', 'created_at', 
            'is_enrolled'
        ]

    def get_thumbnail(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return Urls.STATIC_S3_URL + thumbnail


class CourseLessonPublicViewSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'title', 'description', 
            'duration', 'created_at'
        ]


class CourseLessonEnrolledViewSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'title', 'description', 
            'duration', 'video_url', 'created_at'
        ]

    def get_video_url(self, obj):
        video_key = obj.media_key
        if not video_key or not obj.is_enrolled:
            return None
        return S3Utils.get_signed_url(object_key=video_key, expiration=Units.HOUR * 4)
    

class LessonTextResourceSelectionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    notes = serializers.CharField(required=True)
    related_links = serializers.JSONField(required=True)

    class Meta:
        model = CourseLesson
        fields = [
            'notes', 'related_links'
        ]
    

class LessonFileResourceListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    file_size = serializers.IntegerField(required=True)
    file_type = serializers.CharField(required=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = LessonResource
        fields = [
            'uuid', 'title', 'file_size', 
            'file_type', 'file_url', 'created_at'
        ]

    def get_file_url(self, obj):
        file_key = obj.file_key
        if not file_key:
            return None
        return S3Utils.get_signed_url(obj.file_key, expiration=Units.HOUR * 4)


class EnrolledCoursesListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    uuid = serializers.UUIDField(source='course.uuid')
    title = serializers.CharField(source='course.title')
    description = serializers.CharField(source='course.description', required=True)
    thumbnail = serializers.SerializerMethodField(read_only=True)
    duration = serializers.DecimalField(source='course.duration', max_digits=10, decimal_places=4, required=True)
    created_at = serializers.DateTimeField(source='course.created_at')
    enrolled_at = serializers.DateTimeField(source='created_at')
    
    class Meta:
        model = Enrollments
        fields = [
            'uuid', 'title', 'description',
            'thumbnail', 'duration', 'created_at', 
            'enrolled_at'
        ]

    def get_thumbnail(self, obj):
        thumbnail = obj.course.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return Urls.STATIC_S3_URL + thumbnail