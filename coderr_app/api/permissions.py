from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows only the object owner
    to modify it, while read-only access is allowed for everyone.
    """

    def has_object_permission(self, request, view, obj):
        """
        Grants permission if:
            - The request method is safe (GET, HEAD, OPTIONS), or
            - The requesting user is the owner of the object.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
    



class IsBusinessUser(BasePermission):
    """
    Permission that allows access only to authenticated users
    whose profile type is 'business'.
    """
    def has_permission(self, request, view):
        """
        Grants permission if:
            - The user is authenticated, and
            - The user has a profile, and
            - The profile type is 'business'.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, 'profile'):
            return False

        return user.profile.type == 'business'


class IsOfferOwner(BasePermission):
    """
    Permission that allows access only to the creator (owner)
    of the Offer instance.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    


class IsBusinessOrderOwner(BasePermission):
    """
    Permission that allows only the business user
    associated with the Order to modify its status.
    """
    def has_object_permission(self, request, view, obj):
        """
        Grants permission if:
            - The user is authenticated,
            - The user has a profile of type 'business',
            - The user is the business_user of the Order.
        """
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'profile') or request.user.profile.type != 'business':
            return False

        return obj.business_user == request.user