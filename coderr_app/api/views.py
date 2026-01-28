from rest_framework import viewsets, mixins, filters, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from coderr_app.models import Profile
from .serializers import ProfileSerializer, ProfileUpdateSerializer, BusinessProfileSerializer, CustomerProfileSerializer


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin):
    """
    ViewSet für Profile:
    - list() → alle Profile
    - retrieve() → einzelnes Profile
    - update()/partial_update() → Profile bearbeiten
    - business_profiles → alle Geschäftsnutzer
    - customer_profiles → alle Kundenprofile
    """
    queryset = Profile.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        elif self.action == 'business_profiles':
            return BusinessProfileSerializer
        elif self.action == 'customer_profiles':
            return CustomerProfileSerializer
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

    @action(detail=False, methods=['get'], url_path='business', url_name='business-profiles')
    def business_profiles(self, request):
        """
        Gibt alle Geschäftsnutzer zurück.
        """
        queryset = self.get_queryset().filter(type='business')
        for profile in queryset:
            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                if getattr(profile, field) is None:
                    setattr(profile, field, '')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer', url_name='customer-profiles')
    def customer_profiles(self, request):
        """
        Gibt alle Kundenprofile zurück.
        """
        queryset = self.get_queryset().filter(type='customer')
        for profile in queryset:
            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                if getattr(profile, field) is None:
                    setattr(profile, field, '')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BusinessProfileListView(generics.ListAPIView):
    """
    Gibt eine Liste aller Geschäftsnutzer zurück.
    Felder first_name, last_name, location, tel, description und working_hours
    werden automatisch im Serializer auf '' gesetzt, wenn sie None sind.
    """
    serializer_class = BusinessProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(type='business')