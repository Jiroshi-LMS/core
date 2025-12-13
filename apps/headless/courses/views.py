from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.utilities.BaseView import HeadlessReadOnlyViewSet
from apps.headless.common.utilities.Paginator import DEFAULT_PAGINATION
from apps.headless.common.utilities.Response import success
from apps.headless.common.helpers.pagination_helpers import pagination_selector
from apps.headless.common.permissions.common import InstructorAPIKeyAuthentication, StudentJWTAuthentication
from apps.dashboard.courses.models import Course

from .serializers import (CourseCatalogueSerializer)


class CourseCatalogueViewset(HeadlessReadOnlyViewSet):
    """
    To allow open access to course list and retrival
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    access_type = KEY_TYPES.get('pk')
    serializer_class = CourseCatalogueSerializer
    pagination_class = DEFAULT_PAGINATION

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.instructor, access_status="active")
    
    def paginate_queryset(self, queryset):
        pagination = pagination_selector(self.request.query_params)
        return (pagination.paginate_queryset(queryset, self.request)if pagination 
                else super().paginate_queryset(queryset))
    
    def get_paginator(self):
        paginator = pagination_selector(self.request.query_params)
        return paginator if paginator else self.paginator

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
        return super().retrieve(request, *args, **kwargs)
