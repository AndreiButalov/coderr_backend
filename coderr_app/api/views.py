from rest_framework import viewsets, mixins, status, generics
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.db.models import Avg, Count
from .filters import OfferFilterBackend
from .permissions import IsBusinessUser, IsOfferOwner
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
    ViewSet für Profile:
    - Listet alle Profile
    - Zeigt Details eines Profils
    - Ermöglicht Update (teilweise und komplett) für den eigenen User
    Berechtigungen: Nur authentifizierte User.
    """
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Gibt je nach Aktion den passenden Serializer zurück:
        - Update / Partial Update -> ProfileUpdateSerializer
        - Andere Aktionen -> ProfileSerializer
        """
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        return ProfileSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        Patch-Methode für Profilupdates.
        Prüft, ob der authentifizierte User Besitzer des Profils ist.
        Gibt nach Update die vollständigen Profildaten zurück.
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
    Listet alle Business-Profile.
    Berechtigungen: Authentifizierte User
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):        
        return Profile.objects.filter(type='business')
    


class CustomerProfileListView(generics.ListAPIView):    
    """
    Listet alle Kundenprofile.
    Berechtigungen: Authentifizierte User
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):        
        return Profile.objects.filter(type='customer')
    

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    CRUD View für OfferDetail:
    - Retrieve, Update (partial), Destroy
    Berechtigungen: Authentifizierte User, Update nur durch Besitzer des Angebots
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """
        Überschreibt Update, um nach Änderung des OfferDetail auch das Offer zu serialisieren
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
    ViewSet für Offer:
    - List, Retrieve, Create, Update, Partial Update, Delete
    - Filterung über OfferFilterBackend
    - Pagination via OfferPagination
    Berechtigungen:
        - List / Retrieve: Authentifiziert
        - Create: Authentifiziert + BusinessUser
        - Update / Delete: Authentifiziert + BusinessUser + OfferOwner
    """
    queryset = Offer.objects.all().select_related('user').prefetch_related('details')
    pagination_class = OfferPagination
    filter_backends = [OfferFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        if self.action == 'create':
            return [IsAuthenticated(), IsBusinessUser()]

        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsBusinessUser(), IsOfferOwner()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Gibt Serializer je nach Aktion zurück:
        - Create -> OfferCreateSerializer
        - Update / Partial Update -> OfferUpdateSerializer
        - Retrieve -> OfferDetailViewSerializer
        - Default -> OfferSerializer
        """
        if self.action == 'create':
            return OfferCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        if self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()

        read_serializer = OfferCreateSerializer(
            offer,
            context={'request': request}
        )

        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class OrderView(generics.ListCreateAPIView):
    """
    Listet Orders je nach User-Typ:
    - Kunde: zeigt eigene Bestellungen
    - Business: zeigt eigene Angebote/Orders
    Erstellt Orders aus OfferDetails für Kunden
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.type == 'customer':
                return Order.objects.filter(customer_user=user)
            elif user.profile.type == 'business':
                return Order.objects.filter(business_user=user)
        return Order.objects.none()

    def post(self, request, *args, **kwargs):
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
    Detailansicht einer Order:
    - Patch: Statusupdate für Kunden und Business
    - Delete: nur Admins
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if order.customer_user != user and order.business_user != user:
            return Response({"detail": "Keine Berechtigung."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        order = self.get_object()

        if not request.user.is_staff:
            return Response({"detail": "Keine Berechtigung."}, status=status.HTTP_403_FORBIDDEN)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessOrderCountView(APIView):
    """
    API View zur Abfrage der Anzahl in-progress Orders für einen Business User
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({"detail": "Kein Business User gefunden."}, status=404)

        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})


class BusinessCompletedOrderCountView(APIView):
    """
    API View zur Abfrage der Anzahl abgeschlossener Orders für einen Business User
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)

        if not hasattr(business_user, 'profile') or business_user.profile.type != 'business':
            return Response({"detail": "Kein Business User gefunden."}, status=404)

        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})


class ReviewListView(ListCreateAPIView):
    """
    Listet Reviews und ermöglicht Erstellung neuer Reviews.
    Filterbar nach:
        - business_user_id
        - reviewer_id
        - ordering: rating, updated_at
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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
        return ReviewCreateSerializer if self.request.method == 'POST' else ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=201)


class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    """
    Detailansicht eines Reviews:
    - Patch: Nur Ersteller darf bearbeiten
    - Delete: Nur Ersteller darf löschen
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
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
    Liefert Basisinformationen für die Plattform:
    - Gesamtzahl Reviews
    - Durchschnittliche Bewertung
    - Anzahl Business Profiles
    - Anzahl Offers
    Zugänglich für alle (AllowAny)
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