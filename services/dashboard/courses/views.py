import structlog

from core.decorators import handle_exceptions
from core.utilities import Res, CustomPaginator, S3Utils
from core.constants import ENV, Units
from django.core.serializers import serialize
from django.db import transaction
from django.db.models import Sum
from instructors.permissions import IsOwner
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Course, CourseLesson, LessonResource
from .selectors import CourseSelector, LessonSelector, LessonResourceSelector
from .serializers import (
    CourseSerializer, CourseLessonSerializer, CourseRetrieveSerializer, CourseLessonUpdateSerializer,
    CourseLessonRetrieveSerializer, LessonResourceSerializer, LessonTextResourceSerializer
)

logger = structlog.get_logger(__name__)
course_selector = CourseSelector()
lesson_selector = LessonSelector()
resource_selector = LessonResourceSelector()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated, IsOwner]

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a new course.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = course_selector.create(serializer.validated_data, request.user)
        return Res(
            status.HTTP_201_CREATED, True, 
            data={
                'course_id': course.uuid,
                'created_by': course.created_by.uuid,
            },
            msg="Course created successfully."
        ).json()
    
    @handle_exceptions
    def list(self, request, *args, **kwargs):
        """
            List all courses.
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(created_by=request.user).order_by('-created_at', '-id')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.paginator.get_paginated_response(data=serializer.data, msg="Courses retrieved successfully.")
        
        serializer = self.get_serializer(queryset, many=True)
        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.data,
            msg="Courses retrieved successfully."
        )
    
    @handle_exceptions
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve a course.
        """
        course = self.get_object()
        serializer = CourseRetrieveSerializer(course)
        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.data,
            msg="Course retrieved successfully."
        ).json()
    
    @action(detail=True, methods=['PATCH'], url_path='toggle-status')
    @handle_exceptions
    def toggle_course_activation(self, request, *args, **kwargs):
        """
            Mark a course as active.
        """
        course = self.get_object()
        if course.access_status == 'active':
            course.access_status = 'inactive'
        else:
            lesson_count = lesson_selector.active_lessons(course, request.user).count()
            if lesson_count < 1:
                return Res(
                    status.HTTP_400_BAD_REQUEST, False, 
                    msg="Can't set course as active without any lessons."
                ).json()
        
            course.access_status = 'active'

        course.save()
        return Res(
            status.HTTP_200_OK, True, 
            msg="Course status updated successfully."
        ).json()

    @handle_exceptions
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = self.get_object()
        validated_data = serializer.validated_data

        with transaction.atomic():
            if 'thumbnail' in validated_data and course.thumbnail != validated_data.get('thumbnail'):
                S3Utils.delete_via_object_key(
                    object_keys=[course.thumbnail],
                    bucket_name=ENV.S3_STATIC_BUCKET
                )
            if 'access_status' in validated_data and course.access_status != validated_data.get('access_status'):
                lesson_count = lesson_selector.active_lessons(course, request.user).count()
                if lesson_count < 1:
                    return Res(
                        status.HTTP_400_BAD_REQUEST, False,
                        msg="Can't set course as active without any lessons."
                    ).json()
            course_selector.update(validated_data, course)
        return Res(
            status.HTTP_200_OK, True,
            data=validated_data,
            msg="Course updated successfully."
        ).json()

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        # TODO: Test again after implementing lessons
        course = self.get_object()
        lessons = lesson_selector.all_lessons(course, request.user)

        course.delete()
        for lesson in lessons:
            lesson.delete()

        return Res(
            status.HTTP_501_NOT_IMPLEMENTED, False,
            msg="Course deleted successfully."
        ).json()


class CourseLessonViewSet(ModelViewSet):
    queryset = CourseLesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = CourseLessonSerializer
    pagination_class = CustomPaginator

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a new course lesson.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = course_selector.by_uuid(serializer.validated_data['course_uuid'], request.user)
        lesson = lesson_selector.create(
            serializer.validated_data, request.user, course
        )

        return Res(
            status.HTTP_201_CREATED, True, 
            data={
                'lesson_id': lesson.uuid,
                'created_by': lesson.created_by.uuid,
            },
            msg="Lesson created successfully."
        ).json()

    @handle_exceptions
    def list(self, request, *args, **kwargs):
        """
            List all lessons.
        """
        course_uuid = request.query_params.get('course_id')
        if not course_uuid:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Course ID is required."
            ).json()
        course = course_selector.by_uuid(course_uuid, request.user)
        queryset = self.filter_queryset(self.get_queryset()).order_by('-created_at', '-id')
        queryset = queryset.filter(course=course)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.paginator.get_paginated_response(data=serializer.data, msg="Lessons retrieved successfully.")
        
        serializer = self.get_serializer(queryset, many=True)
        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.data,
            msg="Lessons retrieved successfully."
        )
    
    @handle_exceptions
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve a lesson.
        """
        lesson = self.get_object()
        serializer = CourseLessonRetrieveSerializer(lesson)
        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.data,
            msg="Lesson retrieved successfully."
        ).json()
    
    @action(detail=True, methods=['PATCH'], url_path='update-lesson-media')
    @handle_exceptions
    def update_media_key(self, request, *args, **kwargs):
        """
            Update the media key of a lesson.
        """
        lesson = self.get_object()
        lesson_media = request.data.get('media_key')
        media_duration = request.data.get('media_duration')
        if not lesson_media or not media_duration:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Missing required fields: media_key, media_duration."
            ).json()
        existing_media_key = lesson.media_key
        if existing_media_key and existing_media_key != lesson_media:
            S3Utils.delete_via_object_key(object_keys=[existing_media_key])
        lesson.media_key = lesson_media
        lesson.duration = media_duration
        if lesson.access_status == 'draft':
            lesson.access_status = 'active'
        lesson.save()

        course = course_selector.by_uuid(lesson.course.uuid, request.user)
        course_lessons_duration = lesson_selector.active_lessons(course, request.user).aggregate(
            duration=Sum('duration')
        )['duration']
        if course_lessons_duration is not None:
            course.duration = course_lessons_duration
            if course.access_status == 'draft':
                course.access_status = 'inactive'
            course.save()

        return Res(
            status.HTTP_200_OK, True, 
            msg="Media key updated successfully."
        ).json()
    
    @handle_exceptions
    def update(self, request, *args, **kwargs):
        serializer = CourseLessonUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = self.get_object()
        validated_data = serializer.validated_data

        lesson = lesson_selector.update(validated_data, lesson)
        return Res(
            status.HTTP_200_OK, True, 
            data=validated_data,
            msg="Lesson updated successfully."
        ).json()
    
    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        course = course_selector.by_id(lesson.course_id, request.user)
        course.duration = course.duration - lesson.duration
        if course.duration <= 0:
            course.duration = 0
            course.access_status = 'draft'
            course.save()
        lesson.delete()
        return Res(
            status.HTTP_200_OK, True, 
            msg="Lesson deleted successfully."
        ).json()
    

class LessonResourceViewSet(ModelViewSet):
    queryset = LessonResource.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = LessonResourceSerializer
    pagination_class = CustomPaginator

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"
    
    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a lesson file resource.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = lesson_selector.by_uuid(serializer.validated_data['lesson_uuid'], request.user)
        resource = resource_selector.create(
            serializer.validated_data, lesson, request.user
        )

        return Res(
            status.HTTP_201_CREATED, True, 
            data={
                'resource_id': resource.uuid,
                'lesson_id': lesson.uuid
            },
            msg="Resource created successfully.",
        ).json()
    
    @action(detail=False, methods=['PATCH'], url_path='update-text-resources')
    @handle_exceptions
    def update_text_resources(self, request, *args, **kwargs):
        """
            Create a lesson text resource.
        """
        serializer = LessonTextResourceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        lesson = lesson_selector.by_uuid(validated_data['lesson_uuid'], request.user)
        if validated_data.get('notes'):
            lesson.notes = validated_data.get('notes')
        if validated_data.get('related_links'):
            lesson.related_links = validated_data.get('related_links')
        lesson.save()

        return Res(
            status.HTTP_201_CREATED, True, 
            msg="Text Resource updated successfully."
        ).json()
    
    @handle_exceptions
    def list(self, request, *args, **kwargs):
        """
            List all lesson resources (files and text). 
        """
        lesson_uuid = request.query_params.get('lesson_id')
        if not lesson_uuid:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Lesson ID is required."
            ).json()
        lesson = lesson_selector.by_uuid(lesson_uuid, request.user)
        file_resources = resource_selector.by_lesson(lesson)

        return Res(
            status.HTTP_200_OK, True,
            data={
                'lesson_id': lesson.uuid,
                'notes': lesson.notes,
                'related_links': lesson.related_links,
                'file_resources': [
                    {
                        'uuid': file_resource.uuid,
                        'title': file_resource.title,
                        'file_name': file_resource.file_name,
                        'file_size': file_resource.file_size,
                        'file_type': file_resource.file_type,
                        'file_key': S3Utils.get_signed_url(file_resource.file_key, expiration=Units.DAY),
                    }
                    for file_resource in file_resources
                ],
            },
        ).json()
    
    @handle_exceptions
    def partial_update(self, request, *args, **kwargs):
        """
            Update a lesson file title.
        """
        resource = self.get_object()
        title = request.data.get('title')
        if not title:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Title is required."
            ).json()
        resource.title = title
        resource.save()
        return Res(
            status.HTTP_200_OK, True, 
            msg="Resource updated successfully."
        ).json()

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        """
            Delete a lesson file resource.
        """
        resource = self.get_object()
        file_key = resource.file_key
        if file_key:
            S3Utils.delete_via_object_key(object_keys=[file_key])
        resource.hard_delete()
        return Res(
            status.HTTP_200_OK, True, 
            msg="Resource deleted successfully."
        ).json()
