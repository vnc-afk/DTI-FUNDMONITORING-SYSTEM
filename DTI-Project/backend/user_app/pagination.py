"""Pagination utilities for API endpoints."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from user_app.utils import get_items_per_page


class UserPreferencePageNumberPagination(PageNumberPagination):
    """Use each authenticated user's saved items-per-page preference."""

    page_size = 25
    max_page_size = 200

    def get_page_size(self, request):
        try:
            preferred = int(get_items_per_page(request, default=self.page_size))
        except (TypeError, ValueError):
            preferred = self.page_size

        return max(1, min(preferred, self.max_page_size))

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page": self.page.number,
                "pages": self.page.paginator.num_pages,
                "page_size": self.page.paginator.per_page,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous(),
                "results": data,
            }
        )
