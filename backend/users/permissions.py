from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.method in permissions.SAFE_METHODS or
                    request.user.is_authenticated)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
