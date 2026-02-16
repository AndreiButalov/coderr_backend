from rest_framework.pagination import PageNumberPagination

class OfferPagination(PageNumberPagination):
    """
    Pagination-Klasse für Offer-Listen.

    Einstellungen:
    - page_size: Standardanzahl der Elemente pro Seite (10)
    - page_size_query_param: Query-Parameter zur dynamischen Anpassung der Seitengröße ('page_size')
    - max_page_size: Maximale Elemente pro Seite (100)

    Beispiel:
        GET /offers/?page=2&page_size=20
        -> liefert Seite 2 mit maximal 20 Offers
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100