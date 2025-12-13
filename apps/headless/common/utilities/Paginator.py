from rest_framework.pagination import PageNumberPagination, CursorPagination
from .Response import success


class HeadlessPageNumberPaginator(PageNumberPagination):
    """
    Custom page number pagination class for sending custom responses.
    """
    page_size = 10  # default
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data, msg="Successfully Fetched"):
        return success(data={
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        }, msg=msg)
    

class HeadlessCursorPagination(CursorPagination):
    """
    Custom cursor pagination class for sending custom response
    """
    page_size = 10  # Set the number of items per page
    ordering = '-id' # Default ordering field (must be a unique, unchanging field)
    cursor_query_param = 'cursor' # Customize the query parameter name from 'cursor' to 'cu'
    offset_cutoff = 50  # Max number of items in a page before a hard cutoff

    def get_paginated_response(self, data, msg="Successfully Fetched"):
        return success(data={
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        }, msg=msg)


DEFAULT_PAGINATION = HeadlessCursorPagination

PAGINATION_SELECTOR = {
    'page': HeadlessPageNumberPaginator,
    'cusor': HeadlessCursorPagination
}