from rest_framework.pagination import PageNumberPagination

class OfferPagination(PageNumberPagination):
    """
    Pagination class for Offer list views.

    Configuration:
        - page_size: Default number of items per page (10)
        - page_size_query_param: Query parameter that allows clients
          to dynamically set the page size ('page_size')
        - max_page_size: Maximum number of items allowed per page (100)

    Example:
        GET /offers/?page=2&page_size=20
        -> Returns page 2 with up to 20 offers
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100