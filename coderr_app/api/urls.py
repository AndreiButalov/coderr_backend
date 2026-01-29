from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, BusinessProfileListView, CustomerProfileListView, OfferDetailView,
    OfferViewSet
    )

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)), 
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='business-profiles'),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]