from django.db.models import Q, Min
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError


class OfferFilterBackend(BaseFilterBackend):
    """
    Custom FilterBackend für Offers.
    Fügt Annotationen für min_price und min_delivery_time hinzu und filtert anschließend
    das Queryset basierend auf Request-Query-Parametern.
    """

    def filter_queryset(self, request, queryset, view):
        """
        Filtert das Offer-Queryset basierend auf den Query-Parametern.

        Query-Parameter:
        - creator_id: Integer, Filter nach User-ID des Erstellers
        - min_price: Float, Filter nach minimalem Preis
        - max_delivery_time: Integer, Filter nach maximaler Lieferzeit in Tagen
        - search: String, Suche in Titel oder Beschreibung
        - ordering: Sortierung nach 'updated_at' oder 'min_price', optional '-'

        Validierung:
        - creator_id muss eine Zahl sein
        - min_price muss float konvertierbar sein
        - max_delivery_time muss eine ganze Zahl sein
        - ordering nur erlaubt: updated_at, -updated_at, min_price, -min_price

        Gibt das gefilterte und sortierte Queryset zurück.
        """
        queryset = queryset.annotate(
            min_price_value=Min('details__price'),
            min_delivery_time_value=Min('details__delivery_time_in_days')
        )

        params = request.query_params

        if creator_id := params.get('creator_id'):
            if not creator_id.isdigit():
                raise ValidationError({"creator_id": "Must be an integer."})
            queryset = queryset.filter(user_id=int(creator_id))

        if min_price := params.get('min_price'):
            try:
                min_price = float(min_price)
            except ValueError:
                raise ValidationError({"min_price": "Must be a number."})
            queryset = queryset.filter(min_price_value__gte=min_price)

        if max_delivery_time := params.get('max_delivery_time'):
            if not max_delivery_time.isdigit():
                raise ValidationError({"max_delivery_time": "Must be an integer."})
            queryset = queryset.filter(
                min_delivery_time_value__lte=int(max_delivery_time)
            )

        if search := params.get('search'):
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        if ordering := params.get('ordering'):
            allowed = ['updated_at', '-updated_at', 'min_price', '-min_price']
            if ordering not in allowed:
                raise ValidationError({
                    "ordering": "Allowed: updated_at, -updated_at, min_price, -min_price"
                })

            if 'min_price' in ordering:
                ordering = ordering.replace('min_price', 'min_price_value')

            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset
