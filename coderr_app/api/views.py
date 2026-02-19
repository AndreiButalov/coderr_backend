from rest_framework import viewsets, mixins, status, generics
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.db.models import Avg, Count
from .filters import OfferFilterBackend
from .permissions import IsBusinessUser, IsOfferOwner, IsBusinessOrderOwner
from rest_framework.generics import RetrieveUpdateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from coderr_app.models import Profile, OfferDetail, Offer, Order, Review
from .pagination import OfferPagination
from django.shortcuts import get_object_or_404
from .serializers import (
    ProfileSerializer, ProfileUpdateSerializer, BusinessProfileSerializer, CustomerProfileSerializer, 
    OfferDetailSerializer, OfferSerializer, OfferCreateSerializer, OfferUpdateSerializer, OfferPatchSerializer,
    OfferDetailViewSerializer, OrderSerializer, OrderCreateSerializer, OrderCreateResponseSerializer,
    OrderStatusUpdateSerializer, ReviewSerializer, ReviewCreateSerializer
    )


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin):
    """
    ViewSet for managing Profile instances.

    Supports:
        - Listing all profiles
        - Retrieving profile details
        - Updating (full and partial) the authenticated user's profile

    Permissions:
        - Only authenticated users are allowed.
    """
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'user'
    lookup_url_kwarg = 'user_id'

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the action:

            - update / partial_update -> ProfileUpdateSerializer
            - other actions -> ProfileSerializer
        """
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        Handles PATCH requests for profile updates.

        Ensures that the authenticated user is the owner of the profile.
        After updating, returns the full serialized profile data.
        """
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"detail": "Authentifizierter Benutzer ist nicht der Eigentümer Profils."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProfileUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        read_serializer = ProfileSerializer(
            instance,
            context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)
    

class BusinessProfileListView(generics.ListAPIView):
    """
    Lists all business profiles.

    Permissions:
        - Authenticated users only.
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):      
        """
        Returns all profiles with type 'business'.
        """  
        return Profile.objects.filter(type='business')
    


class CustomerProfileListView(generics.ListAPIView):    
    """
    Lists all customer profiles.

    Permissions:
        - Authenticated users only.
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):     
        """
        Returns all profiles with type 'customer'.
        """   
        return Profile.objects.filter(type='customer')
    

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    CRUD view for OfferDetail:

        - Retrieve
        - Partial update
        - Delete

    Permissions:
        - Authenticated users only
        - Updates allowed only for the offer owner
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Overrides update behavior.

        After updating the OfferDetail, the related Offer
        is serialized and returned instead of the detail itself.
        """
        instance = self.get_object()
        offer = instance.offer
        if offer.user != request.user:
            raise PermissionDenied("Du darfst dieses Angebotsdetail nicht bearbeiten.")

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        offer_serializer = OfferPatchSerializer(offer, context={'request': request})
        return Response(offer_serializer.data, status=status.HTTP_200_OK)


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Offer management.

    Supports:
        - List
        - Retrieve
        - Create
        - Update
        - Partial update
        - Delete

    Features:
        - Filtering via OfferFilterBackend
        - Pagination via OfferPagination

    Permissions:
        - List: Public (AllowAny)
        - Retrieve: Authenticated users
        - Create: Authenticated business users
        - Update/Delete: Authenticated business users who own the offer
    """

    queryset = Offer.objects.all().select_related('user').prefetch_related('details')
    pagination_class = OfferPagination
    filter_backends = [OfferFilterBackend]

    def get_permissions(self):
        """
        Returns permission classes depending on the current action.
        """
        if self.action == 'list':
             return [AllowAny()]

        if self.action == 'retrieve':
            return [IsAuthenticated()]

        if self.action == 'create':
            return [IsAuthenticated(), IsBusinessUser()]

        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBusinessUser(), IsOfferOwner()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer depending on the action:

            - create -> OfferCreateSerializer
            - update / partial_update -> OfferUpdateSerializer
            - retrieve -> OfferDetailViewSerializer
            - default -> OfferSerializer
        """
        if self.action == 'create':
            return OfferCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        if self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        """
        Assigns the authenticated user as the offer owner during creation.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Creates a new Offer including its details.

        Returns the full serialized offer representation
        after successful creation.
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        read_serializer = OfferPatchSerializer(
            offer,
            context={'request': request}
        )

        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class OrderView(generics.ListCreateAPIView):
    """
    Lists and creates Order instances.

    Behavior:
        - Customers see their own orders.
        - Business users see orders related to their offers.
        - Customers can create new orders from OfferDetails.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        """
        Returns orders filtered by the authenticated user's profile type.
        """
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.type == 'customer':
                return Order.objects.filter(customer_user=user)
            elif user.profile.type == 'business':
                return Order.objects.filter(business_user=user)
        return Order.objects.none()

    def post(self, request, *args, **kwargs):
        """
        Creates a new Order from an OfferDetail.

        Only users with profile type 'customer' are allowed
        to create orders.
        """
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        offer_detail = OfferDetail.objects.get(id=serializer.validated_data['offer_detail_id'])
        user = request.user

        if not hasattr(user, 'profile') or user.profile.type != 'customer':
            return Response({"detail": "Nur Kunden können Bestellungen erstellen."}, status=403)

        order = OrderSerializer.create_from_offer_detail(offer_detail, customer_user=user)
        read_serializer = OrderCreateResponseSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(RetrieveUpdateAPIView):
    """
    Detailed view for a single Order.

    - PATCH: Allows status updates (business user only)
    - DELETE: Allowed for admin users only
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBusinessOrderOwner]

    def patch(self, request, *args, **kwargs):
        """
        Updates the order status.

        Only the business owner of the order is allowed
        to modify the status.
        """
        order = self.get_object()
        self.check_object_permissions(request, order)

        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data, status=200)
    
    def delete(self, request, *args, **kwargs):
        """
        Deletes an order.

        Only staff (admin) users are allowed to delete orders.
        """
        order = self.get_object()
        if not request.user.is_staff:
            return Response({"detail": "Keine Berechtigung."}, status=403)
        order.delete()
        return Response(status=204)


class BusinessOrderCountView(APIView):
    """
    Returns the number of 'in_progress' orders
    for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Retrieves the count of active (in_progress) orders
        for the specified business user.
        """
        business_user = get_object_or_404(User, id=business_user_id)

        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({"detail": "Kein Business User gefunden."}, status=404)

        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})


class BusinessCompletedOrderCountView(APIView):
    """
    Returns the number of completed orders
    for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        Retrieves the count of completed orders
        for the specified business user.
        """
        business_user = get_object_or_404(User, id=business_user_id)

        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({"detail": "Kein Business User gefunden."}, status=404)

        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})


class ReviewListView(ListCreateAPIView):
    """
    Lists and creates Review instances.

    Supports filtering by:
        - business_user_id
        - reviewer_id
        - ordering (rating, updated_at)
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns reviews filtered by query parameters.
        """
        queryset = Review.objects.all()
        params = self.request.query_params

        if business_id := params.get('business_user_id'):
            queryset = queryset.filter(business_user_id=business_id)

        if reviewer_id := params.get('reviewer_id'):
            queryset = queryset.filter(reviewer_id=reviewer_id)

        if ordering := params.get('ordering'):
            if ordering.lstrip('-') in ['rating', 'updated_at']:
                queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        """
        Returns ReviewCreateSerializer for POST requests,
        otherwise ReviewSerializer.
        """
        return ReviewCreateSerializer if self.request.method == 'POST' else ReviewSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates a new review and returns the full review representation.
        """
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=201)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """
    Detailed view for a single Review.

    - PATCH: Only the review author can edit
    - DELETE: Only the review author can delete
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Updates rating and/or description.

        Only the review author is allowed to modify the review.
        """
        review = self.get_object()

        if review.reviewer != request.user:
            return Response(
                {"detail": "Du darfst diese Bewertung nicht bearbeiten."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            key: request.data[key]
            for key in ['rating', 'description']
            if key in request.data
        }

        serializer = self.get_serializer(review, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Deletes the review.

        Only the review author is allowed to delete it.
        """
        review = self.get_object()

        if review.reviewer != request.user:
            return Response(
                {"detail": "Du darfst diese Bewertung nicht löschen."},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseInfoView(APIView):
    """
    Provides general platform statistics:

        - Total number of reviews
        - Average rating
        - Number of business profiles
        - Number of offers

    Accessible to everyone (AllowAny).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            review_stats = Review.objects.aggregate(
                review_count=Count('id'),
                average_rating=Avg('rating')
            )
            review_count = review_stats['review_count'] or 0
            average_rating = round(review_stats['average_rating'] or 0, 2)

            business_profile_count = Profile.objects.filter(type='business').count()
            offer_count = Offer.objects.count()

            data = {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            }
            return Response(data, status=200)

        except Exception:
            return Response(
                {"detail": "Interner Serverfehler."},
                status=500
            )        