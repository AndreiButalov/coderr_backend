from django.db.models import Q, Min
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError


class OfferFilterBackend(BaseFilterBackend):
    """
    Custom filter backend for filtering Offer querysets based on query parameters.

    Supported query parameters:

        - creator_id (int): Filters offers by the creator's user ID.
        - min_price (float): Filters offers by minimum detail price (greater than or equal).
        - max_delivery_time (int): Filters offers by maximum delivery time in days.
        - search (str): Case-insensitive search in title and description.
        - ordering (str): Sorting field. Allowed values:
              'updated_at', '-updated_at',
              'min_price', '-min_price'

    Validation:
        - Invalid parameter types raise a 400 ValidationError.
    """

    ALLOWED_ORDERING = ['updated_at', '-updated_at', 'min_price', '-min_price']

    def filter_queryset(self, request, queryset, view):
        """
        Applies all available filters and ordering to the queryset.

        Steps:
            1. Annotate queryset with computed minimum values.
            2. Apply individual filters.
            3. Apply ordering.
        """
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
        """
        Adds computed annotation fields to the queryset:

            - min_price_value: minimum price across related OfferDetails
            - min_delivery_time_value: minimum delivery time across related OfferDetails

        These annotated fields are used for filtering and ordering.
        """
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
        """
        Filters the queryset by creator_id.

        Parameters:
            - creator_id (int): User ID of the offer creator.

        Raises:
            ValidationError: If creator_id is not a valid integer.
        """
        creator_id = params.get('creator_id')
        if creator_id is None:
            return queryset

        if not creator_id.isdigit():
            raise ValidationError({"creator_id": "Must be an integer."})

        return queryset.filter(user_id=int(creator_id))
    

    def _filter_by_min_price(self, queryset, params):
        """
        Filters the queryset by minimum price.

        Parameters:
            - min_price (float): Filters offers whose minimum detail price
              is greater than or equal to the given value.

        Raises:
            ValidationError: If min_price is not a valid float.
        """
        min_price = params.get('min_price')
        if min_price is None:
            return queryset

        try:
            min_price = float(min_price)
        except ValueError:
            raise ValidationError({"min_price": "Must be a float."})

        return queryset.filter(min_price_value__gte=min_price)

    def _filter_by_max_delivery_time(self, queryset, params):
        """
        Filters the queryset by maximum delivery time.

        Parameters:
            - max_delivery_time (int): Maximum allowed minimum delivery time in days.

        Raises:
            ValidationError: If max_delivery_time is not a valid integer.
        """
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
        """
        Applies a case-insensitive search filter on title and description.

        Parameters:
            - search (str): Search keyword.

        Returns:
            Queryset filtered by matching title or description.
        """
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
        """
        Applies ordering to the queryset.

        Default ordering:
            - '-created_at' (newest first)

        Allowed ordering values:
            - 'updated_at'
            - '-updated_at'
            - 'min_price'
            - '-min_price'

        Raises:
            ValidationError: If ordering value is not allowed.
        """
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
