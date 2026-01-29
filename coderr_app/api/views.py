from rest_framework import viewsets, mixins, status, generics
from rest_framework.response import Response
from .pagination import OfferPagination
from coderr_app.models import Profile, OfferDetail, Offer
from .serializers import (
    ProfileSerializer, ProfileUpdateSerializer, BusinessProfileSerializer, CustomerProfileSerializer, 
    OfferDetailSerializer, OfferSerializer
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
    

class OfferDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer



class OfferListView(generics.ListAPIView):
    queryset = Offer.objects.all().order_by('-created_at')
    serializer_class = OfferSerializer
    pagination_class = OfferPagination