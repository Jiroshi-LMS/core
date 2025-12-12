from apps.core.decorators import handle_exceptions
from apps.dashboard.common.utilities.Response import Res
from apps.core.permissions import IsAuthenticated
from apps.dashboard.common.utilities.Paginator import DashboardPageNumberPaginator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import ApiKeys
from .services import APIKeysServices
from .serializers import APIKeyBaseSerializer, APIKeyListSerializer



class APIKeysViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeyBaseSerializer
    pagination_class = DashboardPageNumberPaginator

    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def get_queryset(self):
        return ApiKeys.all_objects.filter(instructor=self.request.user)

    def get_object(self):
        return ApiKeys.all_objects.get(uuid=self.kwargs['uuid'])

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        pub_key_str, pvt_key_str = APIKeysServices.gen_keys(request.user, validated_data)
        return Res(
            code=status.HTTP_201_CREATED,
            data={
                "public": pub_key_str,
                "private": pvt_key_str
            },
            msg="API Keys Generated Successfully !"
        ).json()

    @handle_exceptions
    def list(self, request, *args, **kwargs):
        query = self.filter_queryset(self.get_queryset().order_by('-created_at'))
        page = self.paginate_queryset(query)
        serializer = APIKeyListSerializer(page, many=True)
        return self.paginator.get_paginated_response(
            data=serializer.data, 
            msg="Courses retrieved successfully."
        )

    @handle_exceptions
    def destroy(self, request, *args, **kwargs):
        apikey_instance = self.get_object()
        apikey_instance.hard_delete()
        return Res(
            code=status.HTTP_200_OK,
            msg="API Key has been permanently deleted !"
        ).json()


