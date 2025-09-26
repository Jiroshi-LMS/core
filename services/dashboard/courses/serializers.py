from core.constants import DefaultObjectKeys
from core.utilities import S3Utils
from instructors.models import Instructor
from rest_framework import serializers

from .models import Course, CourseLesson


class CourseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    thumbnail = serializers.CharField(required=True, write_only=True)
    duration = serializers.IntegerField(required=False, default=None)
    access_status = serializers.CharField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'uuid', 'created_at', 'access_status', 'thumbnail_url',
            'title', 'description', 'thumbnail', 'duration', 'created_by'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_thumbnail_url(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return S3Utils.get_signed_url(object_key=thumbnail)


class CourseLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    thumbnail = serializers.CharField(required=False, default=None)
    duration = serializers.IntegerField(required=False, default=None)
    access_status = serializers.CharField(read_only=True)
    # created_by = serializers.PrimaryKeyRelatedField(
    #     read_only=True
    # )
    media_key = serializers.CharField(required=False, default=None, write_only=True)
    course_uuid = serializers.UUIDField(write_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'created_at', 'title', 'access_status',
            'description', 'thumbnail', 'duration', 'created_by',
            'media_key', 'course_uuid', 'thumbnail_url'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_thumbnail_url(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return S3Utils.get_signed_url(object_key=thumbnail)