from rest_framework import viewsets, mixins, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework.generics import ListAPIView
from coderr_app.models import Profile, OfferDetail, Offer, Order
from .pagination import OfferPagination
from .serializers import (
    ProfileSerializer, ProfileUpdateSerializer, BusinessProfileSerializer, CustomerProfileSerializer, 
    OfferDetailSerializer, OfferSerializer, OfferCreateSerializer, OfferUpdateSerializer, OfferPatchSerializer,
    OfferDetailViewSerializer, OrderSerializer, OfferGetDetailSerializer, OrderCreateSerializer
    )


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin):
   
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer        
        return ProfileSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

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
    serializer_class = BusinessProfileSerializer

    def get_queryset(self):        
        return Profile.objects.filter(type='business')
    


class CustomerProfileListView(generics.ListAPIView):    
    serializer_class = CustomerProfileSerializer

    def get_queryset(self):        
        return Profile.objects.filter(type='customer')
    

class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
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
    queryset = Offer.objects.all().order_by('-created_at')
    pagination_class = OfferPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OfferCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OfferUpdateSerializer
        if self.action == 'retrieve':
            return OfferDetailViewSerializer
        return OfferSerializer 



class OrderView(generics.ListCreateAPIView):
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
        read_serializer = OrderSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


#für kürze zeit
class OfferGetDetailListView(ListAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferGetDetailSerializer
    permission_classes = [IsAuthenticated]