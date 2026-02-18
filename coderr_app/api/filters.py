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
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.annotate(
            min_price_value=Min('details__price'),
            min_delivery_time_value=Min('details__delivery_time_in_days')
        )

        params = request.query_params

        creator_id = params.get('creator_id')
        if creator_id is not None:
            if not creator_id.isdigit():
                raise ValidationError({"creator_id": "Must be an integer."})
            queryset = queryset.filter(user_id=int(creator_id))

        min_price = params.get('min_price')
        if min_price is not None:
            try:
                min_price = float(min_price)
            except ValueError:
                raise ValidationError({"min_price": "Must be a float."})
            queryset = queryset.filter(min_price_value__gte=min_price)

        max_delivery_time = params.get('max_delivery_time')
        if max_delivery_time is not None:
            if not max_delivery_time.isdigit():
                raise ValidationError({"max_delivery_time": "Must be an integer."})
            max_delivery_time = int(max_delivery_time)
            queryset = queryset.filter(min_delivery_time_value__isnull=False,
                                       min_delivery_time_value__lte=max_delivery_time)

        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        ordering = params.get('ordering')
        if ordering:
            allowed = ['updated_at', '-updated_at', 'min_price', '-min_price']
            if ordering not in allowed:
                raise ValidationError({
                    "ordering": f"Allowed: {', '.join(allowed)}"
                })
            if 'min_price' in ordering:
                ordering = ordering.replace('min_price', 'min_price_value')
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset