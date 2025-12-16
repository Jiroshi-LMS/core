from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.dashboard.courses.models import Course, CourseLesson
from apps.headless.common.permissions.common import (InstructorAPIKeyAuthentication, StudentJWTAuthentication, 
                                                     IsAuthenticatedStudent)
from apps.headless.common.utilities.BaseView import HeadlessReadOnlyViewSet, HeadlessAPIView, HeadlessGenericView
from apps.headless.common.utilities.Response import success
from apps.headless.common.utilities.Errors import InputValidationError, NotFoundError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    ListModelMixin
)

from .filterset import CourseFilters, CourseLessonFilters, EnrolledCourseFilters
from .serializers import (CourseCatalogueSerializer, CourseLessonPublicViewSerializer, 
                          CourseLessonEnrolledViewSerializer, EnrolledCoursesListSerializer)
from .services import (CourseServices, CourseEnrollmentService, 
                       CourseLessonServices, LessonResourceServices,)


class CourseCatalogueViewset(HeadlessReadOnlyViewSet):
    """
    To allow open access to course list and retrival
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    serializer_class = CourseCatalogueSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilters
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        base_queryset = CourseServices.get_course_catalogue_queryset(self.request.instructor)
        student = getattr(self.request, 'student', None)
        return CourseServices.enrich_with_enrollment_status(base_queryset, student)

    def get_object(self):
        uuid = self.kwargs.get('uuid')
        if not uuid:
            raise InputValidationError("UUID not provided !")
        base_queryset = CourseServices.get_course_catalogue_queryset(self.request.instructor, uuid)
        student = getattr(self.request, 'student', None)
        base_queryset = CourseServices.enrich_with_enrollment_status(base_queryset, student)
        try:
            return base_queryset.get()
        except Course.DoesNotExist:
            raise NotFoundError("Course not found!")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            paginator = self.get_paginator()
            return paginator.get_paginated_response(data=serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success(data=serializer.data, msg="Successfully fetched !")

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(instance=course)
        return success(data=serializer.data, msg="Successfully fetched !")
    

class CourseLessonViewset(HeadlessReadOnlyViewSet):
    """
    Course Lessons View Endpoints
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    serializer_class = CourseLessonPublicViewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseLessonFilters
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'duration']
    ordering = ['-created_at']

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        course_uuid = self.kwargs.get('course_uuid')
        return CourseLessonServices.get_course_lesson_queryset(course_uuid, self.request.instructor)
    
    def get_object(self):
        course_uuid = self.kwargs.get('course_uuid')
        lesson_uuid = self.kwargs.get('lesson_uuid')
        student = getattr(self.request, 'student', None)
        base_queryset = CourseLessonServices.get_course_lesson_queryset(
            course_uuid, self.request.instructor, lesson_uuid
        )
        base_queryset = CourseLessonServices.enrich_with_enrollment_status(base_queryset, student)
        try:
            return base_queryset.get()
        except CourseLesson.DoesNotExist:
            raise NotFoundError("Lesson not found!")
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            paginator = self.get_paginator()
            return paginator.get_paginated_response(data=serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success(data=serializer.data, msg="Successfully fetched !")
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = CourseLessonEnrolledViewSerializer(instance=lesson)
        return success(data=serializer.data, msg="Successfully fetched !")


class LessonResourcesView(HeadlessAPIView):
    """
    API to fetch lesson resources
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    permission_classes = [IsAuthenticatedStudent]

    def get(self, request, course_uuid, lesson_uuid):
        """
            List all lesson resources (files and text). 
        """
        list_data = LessonResourceServices.get_lesson_resources(
            lesson_uuid, course_uuid, request.student, request.instructor,
        )
        return success(
            data=list_data,
            msg="Resources Fetched Successfully"
        )


class CourseEnrollmentView(HeadlessAPIView):
    """
    API to enroll student to a course
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    permission_classes = [IsAuthenticatedStudent]

    def post(self, request):
        course_uuid = request.data.get("course_uuid")
        if not course_uuid:
            raise InputValidationError("Course UUID missing !")
        
        enrollment = CourseEnrollmentService.enroll_student(request.student, course_uuid, request.instructor)
        return success(data={
            "enrollment_id": enrollment.uuid
        }, msg="Enrolled successfully !", code=201)
    

class StudentEnrolledCoursesView(ListModelMixin, HeadlessGenericView):
    """
    API for listing all the courses enrolled by student
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    permission_classes = [IsAuthenticatedStudent]
    serializer_class = EnrolledCoursesListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EnrolledCourseFilters
    search_fields = ['course__title', 'course__description']
    ordering_fields = {
        'enrolled_at': 'created_at',
        'created_at': 'course__created_at',
        'duration': 'course__duration',
    }
    ordering = ['-created_at']

    def get_queryset(self):
        return CourseEnrollmentService.get_enrolled_courses_list(self.request.student, self.request.instructor)

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            paginator = self.get_paginator()
            return paginator.get_paginated_response(data=serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success(data=serializer.data, msg="Successfully fetched !")
        
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
