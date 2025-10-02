from core.constants import DefaultObjectKeys, ENV
from core.utilities import S3Utils
from instructors.models import Instructor
from rest_framework import serializers

from .models import Course, CourseLesson



class CourseLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.IntegerField(required=False, default=None)
    access_status = serializers.CharField(read_only=True)
    media_key = serializers.CharField(required=False, default=None, write_only=True)
    course_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'created_at', 'title', 'access_status',
            'description', 'duration', 'media_key', 'course_uuid'
        ]
        read_only_fields = ['uuid', 'created_at']


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
    enrollments = serializers.SerializerMethodField(read_only=True)

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
        return S3Utils.get_signed_url(
            bucket_name=ENV.S3_STATIC_BUCKET,
            object_key=thumbnail,
        )

    def get_enrollments(self, obj):
        # TODO: Implement Enrollments Count
        return 0


class CourseRetrieveSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.IntegerField(required=False, default=None)
    access_status = serializers.CharField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    enrollments = serializers.SerializerMethodField()

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
        return S3Utils.get_signed_url(
            bucket_name=ENV.S3_STATIC_BUCKET,
            object_key=thumbnail,
        )

    def get_enrollments(self, obj):
        # TODO: Implement Enrollments
        return 0