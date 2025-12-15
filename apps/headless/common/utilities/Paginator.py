from rest_framework.pagination import PageNumberPagination, CursorPagination
from .Response import success


class HeadlessPageNumberPaginator(PageNumberPagination):
    """
    Custom page number pagination class for sending custom responses.
    """
    page_size = 20  # default
    page_size_query_param = 'page_size'
    max_page_size = 150

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
    page_size = 20  # Set the number of items per page
    ordering = '-id' # Default ordering field (must be a unique, unchanging field)
    cursor_query_param = 'cursor' # Customize the query parameter name from 'cursor' to 'cu'
    offset_cutoff = 3000  # Max number of items in a page before a hard cutoff

    def get_paginated_response(self, data, msg="Successfully Fetched"):
        next_link = self.get_next_link()
        prev_link = self.get_previous_link()

        # Extract the raw cursor value from the full URLs
        next_cursor = self.extract_cursor_from_url(next_link) if next_link else None
        prev_cursor = self.extract_cursor_from_url(prev_link, is_previous=True) if prev_link else None

        return success(data={
            "next": next_link,
            "previous": prev_link,
            "next_cursor": next_cursor,
            "previous_cursor": prev_cursor,
            "results": data
        }, msg=msg)


DEFAULT_PAGINATION = HeadlessCursorPagination

PAGINATION_SELECTOR = {
    'page': HeadlessPageNumberPaginator(),
    'cusor': HeadlessCursorPagination()
}