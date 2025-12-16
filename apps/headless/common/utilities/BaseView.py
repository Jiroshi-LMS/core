from apps.headless.common.helpers.pagination_helpers import pagination_selector
from apps.headless.common.utilities.Paginator import DEFAULT_PAGINATION
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .Exceptions import headless_exception_handler



#######################
# Base Headless Views
#######################

class HeadlessAPIView(APIView):
    def handle_exception(self, exc):
        """
        Override DRF's exception pipeline and force it to use our custom handler.
        """
        response = headless_exception_handler(exc, {"view": self})
        if response is not None:
            return response
        return super().handle_exception(exc)
    
    
class HeadlessModelViewSet(ModelViewSet):
    pagination_class = DEFAULT_PAGINATION
    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def handle_exception(self, exc):
        """
        Override DRF's exception handling for ViewSets
        to use the headless error response format.
        """
        response = headless_exception_handler(exc, {"view": self})

        if response is not None:
            return response

        return super().handle_exception(exc)
    
    def paginate_queryset(self, queryset):
        pagination = pagination_selector(self.request.query_params)
        return (pagination.paginate_queryset(queryset, self.request)if pagination 
                else super().paginate_queryset(queryset))
    
    def get_paginator(self):
        paginator = pagination_selector(self.request.query_params)
        return paginator if paginator else self.paginator
    
    def get_serializer(self, *args, **kwargs):
        selections_param = self.request.query_params.get("selections")
        
        if selections_param:
            fields = [field.strip() for field in selections_param.split(",") if field.strip()]
            kwargs["fields"] = fields

        return super().get_serializer(*args, **kwargs)
    

class HeadlessReadOnlyViewSet(ReadOnlyModelViewSet):
    pagination_class = DEFAULT_PAGINATION
    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"
    
    def handle_exception(self, exc):
        """
        Override DRF's exception handling for ReadOnlyViewSets
        to use the headless error response format.
        """
        response = headless_exception_handler(exc, {"view": self})

        if response is not None:
            return response

        return super().handle_exception(exc)
    
    def paginate_queryset(self, queryset):
        pagination = pagination_selector(self.request.query_params)
        return (pagination.paginate_queryset(queryset, self.request)if pagination 
                else super().paginate_queryset(queryset))
    
    def get_paginator(self):
        paginator = pagination_selector(self.request.query_params)
        return paginator if paginator else self.paginator
    
    def get_serializer(self, *args, **kwargs):
        selections_param = self.request.query_params.get("selections")
        
        if selections_param:
            fields = [field.strip() for field in selections_param.split(",") if field.strip()]
            kwargs["fields"] = fields

        return super().get_serializer(*args, **kwargs)
    

class HeadlessGenericView(GenericAPIView):
    pagination_class = DEFAULT_PAGINATION
    lookup_field = 'uuid'
    lookup_value_regex = "[0-9a-f-]+"

    def handle_exception(self, exc):
        """
        Override DRF's exception handling for ReadOnlyViewSets
        to use the headless error response format.
        """
        response = headless_exception_handler(exc, {"view": self})
        if response is not None:
            return response
        return super().handle_exception(exc)
    
    def paginate_queryset(self, queryset):
        pagination = pagination_selector(self.request.query_params)
        return (pagination.paginate_queryset(queryset, self.request)if pagination 
                else super().paginate_queryset(queryset))
    
    def get_paginator(self):
        paginator = pagination_selector(self.request.query_params)
        return paginator if paginator else self.paginator
    
    def get_serializer(self, *args, **kwargs):
        selections_param = self.request.query_params.get("selections")
        
        if selections_param:
            fields = [field.strip() for field in selections_param.split(",") if field.strip()]
            kwargs["fields"] = fields

        return super().get_serializer(*args, **kwargs)
    

##########################
# Dynamic Headless Views
##########################

class DynamicAPIView(HeadlessAPIView):
    selection_options = []