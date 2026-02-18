from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: nur der Besitzer darf sein Profil bearbeiten
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
    



class IsBusinessUser(BasePermission):
    """
    Erlaubt Zugriff nur für User mit profile.type == 'business'
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, 'profile'):
            return False

        return user.profile.type == 'business'


class IsOfferOwner(BasePermission):
    """
    Erlaubt Zugriff nur für den Ersteller des Offers
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    


class IsBusinessOrderOwner(BasePermission):
    """
    Nur der Business-User der Order darf den Status ändern.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'profile') or request.user.profile.type != 'business':
            return False

        return obj.business_user == request.user