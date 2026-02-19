from django.db.models import Q, Min
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError


class OfferFilterBackend(BaseFilterBackend):
    """
    Filtert Offer-Queryset nach Query-Parametern:

    - creator_id: integer
    - min_price: float
    - max_delivery_time: integer
    - search: string
    - ordering: 'updated_at', '-updated_at', 'min_price', '-min_price'

    Validierung: falsche Typen -> 400
    """

    ALLOWED_ORDERING = ['updated_at', '-updated_at', 'min_price', '-min_price']

    def filter_queryset(self, request, queryset, view):
        queryset = self._annotate_queryset(queryset)
        params = request.query_params

        queryset = self._filter_by_creator(queryset, params)
        queryset = self._filter_by_min_price(queryset, params)
        queryset = self._filter_by_max_delivery_time(queryset, params)
        queryset = self._filter_by_search(queryset, params)
        queryset = self._apply_ordering(queryset, params)

        return queryset
    
    """
    # -------------------------
    # Annotation
    # -------------------------
    # """

    def _annotate_queryset(self, queryset):
        return queryset.annotate(
            min_price_value=Min('details__price'),
            min_delivery_time_value=Min('details__delivery_time_in_days')
        )
    """
    # -------------------------
    # Einzelne Filtermethoden
    # -------------------------
    # """

    def _filter_by_creator(self, queryset, params):
        creator_id = params.get('creator_id')
        if creator_id is None:
            return queryset

        if not creator_id.isdigit():
            raise ValidationError({"creator_id": "Must be an integer."})

        return queryset.filter(user_id=int(creator_id))
    

    def _filter_by_min_price(self, queryset, params):
        min_price = params.get('min_price')
        if min_price is None:
            return queryset

        try:
            min_price = float(min_price)
        except ValueError:
            raise ValidationError({"min_price": "Must be a float."})

        return queryset.filter(min_price_value__gte=min_price)

    def _filter_by_max_delivery_time(self, queryset, params):
        max_delivery_time = params.get('max_delivery_time')
        if max_delivery_time is None:
            return queryset

        if not max_delivery_time.isdigit():
            raise ValidationError({"max_delivery_time": "Must be an integer."})

        max_delivery_time = int(max_delivery_time)

        return queryset.filter(
            min_delivery_time_value__isnull=False,
            min_delivery_time_value__lte=max_delivery_time
        )

    def _filter_by_search(self, queryset, params):
        search = params.get('search')
        if not search:
            return queryset

        return queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    """
    # -------------------------
    # Ordering
    # -------------------------
    """
    def _apply_ordering(self, queryset, params):
        ordering = params.get('ordering')

        if not ordering:
            return queryset.order_by('-created_at')

        if ordering not in self.ALLOWED_ORDERING:
            raise ValidationError({
                "ordering": f"Allowed: {', '.join(self.ALLOWED_ORDERING)}"
            })

        if 'min_price' in ordering:
            ordering = ordering.replace('min_price', 'min_price_value')

        return queryset.order_by(ordering)
