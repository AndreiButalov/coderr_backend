from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, BusinessProfileListView, CustomerProfileListView, OfferDetailView,
    OfferListView
    )

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)), 
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='business-profiles'),
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]