import structlog

from core.decorators import handle_exceptions
from core.utilities import Res, CustomPaginator, S3Utils
from core.constants import ENV
from django.db.models import Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Course, CourseLesson
from .selectors import CourseSelector, LessonSelector
from .serializers import CourseSerializer, CourseLessonSerializer


logger = structlog.get_logger(__name__)
course_selector = CourseSelector()
lesson_selector = LessonSelector()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

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
        queryset = self.filter_queryset(self.get_queryset()).order_by('-created_at', '-id')

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
        serializer = self.get_serializer(course)
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
            lesson_count = lesson_selector.active_lessons(course).count()
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


class CourseLessonViewSet(ModelViewSet):
    queryset = CourseLesson.objects.all()
    permission_classes = [IsAuthenticated]
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
        course = course_selector.by_uuid(serializer.validated_data['course_uuid'])
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
        course = course_selector.by_uuid(course_uuid)
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
        serializer = self.get_serializer(lesson)
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
        
        lesson.media_key = lesson_media
        lesson.duration = media_duration
        lesson.access_status = 'active'
        lesson.save()

        course = course_selector.by_uuid(lesson.course.uuid)
        course_lessons_duration = lesson_selector.active_lessons(course).aggregate(
            duration=Sum('duration')
        )['duration']
        if course_lessons_duration is not None:
            course.duration = course_lessons_duration
            course.save()

        return Res(
            status.HTTP_200_OK, True, 
            msg="Media key updated successfully."
        ).json()