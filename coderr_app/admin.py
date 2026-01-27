from django.contrib import admin
from .models import Profile, Offer, OfferDetail, Order, Review


class CustomerProfile(admin.ModelAdmin):
    list_display=['first_name', 'last_name']



admin.site.register(Profile)
admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Order)
admin.site.register(Review)
