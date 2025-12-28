import structlog

from apps.core.decorators import handle_exceptions
from apps.core.permissions import IsAuthenticated
from apps.core.throttles.dashboard_throttle import InstructorRateThrottle
from apps.dashboard.common.utilities.Response import Res
from apps.dashboard.common.utilities.Paginator import DashboardPageNumberPaginator
from apps.headless.courses.models import Enrollments
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from apps.dashboard.instructors.permissions import IsOwner
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from .filters import CourseFilters, LessonFilters, EnrollmentFilters
from .models import Course, CourseLesson, LessonResource
from .selectors import CourseSelector, LessonSelector, LessonResourceSelector
from .serializers import (
    CourseSerializer, CourseUpdateSerializer, 
    CourseLessonSerializer, CourseRetrieveSerializer, 
    CourseLessonUpdateSerializer, CourseLessonRetrieveSerializer, 
    LessonResourceSerializer, LessonTextResourceSerializer,
    EnrollmentsListSerializer
)
from .services import (
    CourseServices, CourseLessonServices,
    LessonResourceServices
)

logger = structlog.get_logger(__name__)
lesson_selector = LessonSelector()
resource_selector = LessonResourceSelector()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = DashboardPageNumberPaginator
    permission_classes = [IsAuthenticated, IsOwner]
    throttle_classes = [InstructorRateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilters
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'duration', 'enrollments_count']
    ordering = ['-created_at']

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.user).annotate(
            enrollments_count=Count('enrollments')
        )
    
    def get_object(self):
        uuid = self.kwargs.get('uuid')
        if uuid:
            return Course.objects.annotate(
                enrollments_count=Count('enrollments')
            ).get(uuid=uuid, created_by=self.request.user)
        return super().get_object()

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a new course.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = CourseServices.create(
            serializer.validated_data, 
            request.user
        )
        return Res(
            status.HTTP_201_CREATED, True, 
            data={'course_id': course.uuid,'created_by': course.created_by.uuid},
            msg="Course created successfully."
        ).json()
    
    @handle_exceptions
    def list(self, request, *args, **kwargs):
        """
            List all courses.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(
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
        course =  CourseServices.toggle_activation(course, request.user)
        return Res(
            status.HTTP_200_OK, True,
            data={"course_id": course.uuid, "access_status": course.access_status},
            msg="Course status updated successfully."
        ).json()

    @handle_exceptions
    def update(self, request, *args, **kwargs):
        """
            Update a Course Info
        """
        serializer = CourseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = self.get_object()
        course = CourseServices.update_course_info(
            serializer.validated_data, course, request.user
        )
        return Res(
            status.HTTP_200_OK, True,
            data={"course_id": course.uuid},
            msg="Course updated successfully."
        ).json()

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        """
            Soft Delete a Course
        """
        course = self.get_object()
        CourseServices.soft_delete_course(course, request.user)
        return Res(
            status.HTTP_200_OK, True,
            msg="Course deleted successfully."
        ).json()


class CourseLessonViewSet(ModelViewSet):
    queryset = CourseLesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    throttle_classes = [InstructorRateThrottle]
    serializer_class = CourseLessonSerializer
    pagination_class = DashboardPageNumberPaginator
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LessonFilters
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        return CourseLesson.objects.filter(created_by=self.request.user)
    
    def get_object(self):
        uuid = self.kwargs.get('uuid')
        if uuid:
            return CourseLesson.objects.get(uuid=uuid, created_by=self.request.user)
        return super().get_object()

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a new course lesson.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = CourseLessonServices.create(serializer.validated_data, request.user)
        return Res(
            status.HTTP_201_CREATED, True, 
            data={'lesson_id': lesson.uuid,'created_by': lesson.created_by.uuid},
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
        course = CourseSelector.by_uuid(course_uuid, request.user)
        queryset = self.filter_queryset(self.get_queryset().filter(course=course))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(data=serializer.data, msg="Lessons retrieved successfully.")
    
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
        media_duration = float(request.data.get('media_duration'))
        media_size = int(request.data.get('media_size'))
        if not lesson_media or not media_duration or not media_size:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Missing required fields: media_key, media_duration, media_size."
            ).json()
        lesson, course = CourseLessonServices.update_lesson_media(
            lesson_media, media_duration, media_size, lesson, request.user
        )
        return Res(
            status.HTTP_200_OK, True, 
            data={"lesson_id": lesson.uuid, "course_id": course.uuid},
            msg="Media key updated successfully."
        ).json()
    
    @handle_exceptions
    def update(self, request, *args, **kwargs):
        serializer = CourseLessonUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = self.get_object()
        CourseLessonServices.update_lesson(serializer.validated_data, lesson)
        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.validated_data,
            msg="Lesson updated successfully."
        ).json()
    
    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        CourseLessonServices.soft_delete_lesson(lesson, request.user)
        return Res(
            status.HTTP_200_OK, True, 
            msg="Lesson deleted successfully."
        ).json()
    

class LessonResourceViewSet(ModelViewSet):
    queryset = LessonResource.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]
    throttle_classes = [InstructorRateThrottle]
    serializer_class = LessonResourceSerializer
    pagination_class = DashboardPageNumberPaginator

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        return LessonResource.objects.filter(created_by=self.request.user)
    
    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a lesson file resource.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource, lesson = LessonResourceServices.create(serializer.validated_data, request.user)
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
        lesson = LessonResourceServices.update_text_resource(validated_data, request.user)
        return Res(
            status.HTTP_200_OK, True, 
            data={"lesson_id": lesson.uuid},
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
        list_data = LessonResourceServices.list_resources(lesson_uuid, request.user)
        return Res(
            status.HTTP_200_OK, True,
            data=list_data,
            msg="Resources Fetched Successfully"
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
        LessonResourceServices.destroy_resource(resource)
        return Res(
            status.HTTP_200_OK, True, 
            msg="Resource deleted successfully."
        ).json()


class EnrollmentsView(ListAPIView):
    """
    List view for enrollments
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [InstructorRateThrottle]
    serializer_class = EnrollmentsListSerializer
    pagination_class = DashboardPageNumberPaginator
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EnrollmentFilters
    search_fields = ['student__identifier', 'course__title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Enrollments.objects.select_related('course', 'student').filter(
            course__created_by=self.request.user
        )

    @handle_exceptions
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.paginator.get_paginated_response(data=serializer.data, msg="Enrollments fetched !")