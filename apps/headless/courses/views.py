from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.utilities.BaseView import HeadlessReadOnlyViewSet, HeadlessAPIView
from apps.headless.common.utilities.Response import success
from apps.headless.common.utilities.Errors import InputValidationError
from apps.headless.common.permissions.common import InstructorAPIKeyAuthentication, StudentJWTAuthentication, IsAuthenticatedStudent
from apps.dashboard.courses.models import Course

from .serializers import (CourseCatalogueSerializer)
from .services import CourseEnrollmentService


class CourseCatalogueViewset(HeadlessReadOnlyViewSet):
    """
    To allow open access to course list and retrival
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    serializer_class = CourseCatalogueSerializer

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.instructor, access_status="active")
    
    def get_object(self):
        uuid = self.kwargs.get('uuid')
        if uuid:
            return Course.objects.get(uuid=uuid, created_by=self.request.instructor, access_status="active")
        return super().get_object()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by('-created_at'))
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
