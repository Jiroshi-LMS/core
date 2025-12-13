from rest_framework import serializers
from apps.core.constants import DefaultObjectKeys, Urls
from apps.dashboard.courses.models import Course
from apps.headless.common.utilities.DynamicSerializerSelector import DynamicFieldsMixin


class CourseCatalogueSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    required_fields = ['is_enrolled']

    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    thumbnail = serializers.SerializerMethodField(read_only=True)
    duration = serializers.DecimalField(max_digits=10, decimal_places=4, required=True)
    is_enrolled = serializers.BooleanField(read_only=True)

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

    # def get_enrollments(self, obj):
    #     # TODO: Implement Enrollments Count once students are implemented
    #     return 0
