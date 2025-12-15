from rest_framework import serializers
from apps.core.constants import DefaultObjectKeys, Urls
from apps.core.utilities import S3Utils
from apps.dashboard.courses.models import Course, CourseLesson
from apps.headless.common.utilities.DynamicSerializerSelector import DynamicFieldsMixin


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
        return S3Utils.get_signed_url(object_key=video_key, expiration=3600)