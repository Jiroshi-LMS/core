from rest_framework.pagination import PageNumberPagination
from .Response import Res

class CustomPaginator(PageNumberPagination):
    """
    Custom pagination class for sending custom responses.
    """
    page_size = 10  # default
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data, msg="Successfully Fetched"):
        return Res(data={
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        }, msg=msg).json()