from apps.headless.common.utilities.BaseView import HeadlessReadOnlyViewSet
from apps.headless.common.permissions.common import IsValidInstructor, StudentJWTAuthentication
from apps.dashboard.courses.models import Course

from .serializers import (CourseCatalogueSerializer)


class CourseCatalogueViewset(HeadlessReadOnlyViewSet):
    """
    To allow open access to course list and retrival
    """
    # authentication_classes = [StudentJWTAuthentication]
    permission_classes = [IsValidInstructor]
    serializer_class = CourseCatalogueSerializer

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.instructor)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
