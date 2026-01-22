from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from coderr_app.models import Profile
from .serializers import ProfileSerializer




class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin):
    """
    Profile API:
    - GET /api/profile/{pk}/
    - PATCH /api/profile/{pk}/
    - GET /api/profiles/business/
    - GET /api/profiles/customer/
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    # filter_backends = [filters.SearchFilter]
    # search_fields = ['type', 'location', 'user__username']

    def get_queryset(self):
        """
        Optional: filter nach type, z.B. business/customer
        """
        profile_type = self.request.query_params.get('type')
        qs = super().get_queryset()
        if profile_type in ['business', 'customer']:
            qs = qs.filter(type=profile_type)
        return qs
