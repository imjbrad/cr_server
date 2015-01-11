__author__ = 'jordanbradley'

from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    # based on http://www.django-rest-framework.org/api-guide/permissions/#object-level-permissions

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user


class IsOwnerOrNoPermissions (permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # the api will restrict all methods unless the current user
        # owns the object
        return obj.user == request.user
