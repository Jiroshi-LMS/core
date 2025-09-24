import structlog

from core.decorators import handle_exceptions
from core.utilities import Res, CustomPaginator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Course, CourseLesson
from .selectors import CourseSelector, LessonSelector
from .serializers import CourseSerializer, CourseLessonSerializer


logger = structlog.get_logger(__name__)
course_selector = CourseSelector()
lesson_selector = LessonSelector()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = [CustomPaginator]
    permission_classes = [IsAuthenticated]

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
        queryset = self.filter_queryset(self.get_queryset()).order_by('-created_at')

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


class CourseLessonViewSet(ModelViewSet):
    queryset = CourseLesson.objects.all()
    serializer_class = CourseLessonSerializer
    permission_classes = [IsAuthenticated]

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
        queryset = self.filter_queryset(self.get_queryset()).order_by('-created_at')

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