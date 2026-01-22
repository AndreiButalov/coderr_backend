from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    file = models.CharField(blank=True, null=True) # hier andere fiels 
    tel = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.type})"
    

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.CharField(blank=True, null=True) # hier andere fiels
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    OFFER_TYPES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='details'
    )
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.PositiveIntegerField()
    revisions = models.PositiveIntegerField(default=0)
    features = models.JSONField(default=list)

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type}"
    


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_orders'
    )
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='business_orders'
    )
    offer = models.ForeignKey(
        Offer, on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.title}"


class Review(models.Model):
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    customer_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='given_reviews'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
