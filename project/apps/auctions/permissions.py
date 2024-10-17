from rest_framework import permissions

class IsBuyerOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.isBuyer()
        )

    def has_object_permission(self, request, view, obj):
        return bool(request.user and obj.owner == request.user)
