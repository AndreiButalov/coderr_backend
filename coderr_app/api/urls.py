from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, BusinessProfileListView, CustomerProfileListView, OfferDetailView,
    OfferViewSet, OrderView, OrderDetailView, BusinessCompletedOrderCountView,
    BusinessOrderCountView, ReviewListView, ReviewDetailView, BaseInfoView
    )

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)), 
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='business-profiles'),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('orders/', OrderView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-count/<int:business_user_id>/', BusinessOrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', BusinessCompletedOrderCountView.as_view(), name='completed-order-count'),
    path('reviews/', ReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]