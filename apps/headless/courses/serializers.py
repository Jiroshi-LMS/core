from rest_framework import serializers
from apps.core.constants import DefaultObjectKeys, Urls
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
            'uuid', 'created_at', 'title', 'description',
            'thumbnail', 'duration', 'is_enrolled'
        ]

    def get_thumbnail(self, obj):
        thumbnail = obj.thumbnail
        if not thumbnail:
            thumbnail = DefaultObjectKeys.THUMBNAIL
        return Urls.STATIC_S3_URL + thumbnail


class CourseLessonPublicListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, default="")
    duration = serializers.DecimalField(default=0, max_digits=10, decimal_places=4, required=False)
    media_size = serializers.IntegerField(read_only=True)

    class Meta:
        model = CourseLesson
        fields = [
            'uuid', 'title', 'description', 
            'duration', 'media_size', 'created_at'
        ]