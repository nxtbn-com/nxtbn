from django.conf import settings
from django.db.models.aggregates import Count
from django.db.models import Q

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class NxtbnPagination(PageNumberPagination):
    """
    Custom pagination class for Django REST Framework that allows for configurable
    page sizes. The page size can be set at the view level, and it defaults to `default_page_size`.
    """

    default_page_size = 20  # Default number of items per page

    def __init__(self, page_size=None):
        """
        Initialize the pagination class with an optional page size.
        
        :param page_size: Optional; the number of items per page. If not specified,
                          it defaults to `default_page_size`.
        """
        self.page_size = page_size or self.default_page_size
        super().__init__()

    def get_paginated_response(self, data):
        """
        Returns a paginated response with the given data.
        
        :param data: The paginated data to be returned in the response.
        :return: A `Response` object containing pagination details and the results.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('current_pagination_step', self.get_html_context()),
            ('current_page', self.page.number),
            ('next_page_url', self.get_next_link()),
            ('next_page_number', self.get_next_number()),
            ('previous_page_url', self.get_previous_link()),
            ('previous_page_number', self.get_previous_number()),
            ('total_pages', self.page.paginator.num_pages),
            ('results', data),
        ]))

    def get_previous_number(self):
        """
        Returns the page number of the previous page, if it exists.
        
        :return: The previous page number, or `None` if there is no previous page.
        """
        if not self.page.has_previous():
            return None
        previous_number = self.page.previous_page_number()
        return previous_number if previous_number >= 1 else None
    
    def get_next_number(self):
        """
        Returns the page number of the next page, if it exists.
        
        :return: The next page number, or `None` if there is no next page.
        """
        if not self.page.has_next():
            return None
        next_number = self.page.next_page_number()
        return next_number if next_number >= 1 else None
