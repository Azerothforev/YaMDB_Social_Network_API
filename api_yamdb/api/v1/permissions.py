from rest_framework.permissions import (
    BasePermission, IsAdminUser, SAFE_METHODS)


class DeleteGetPatchPermission(BaseException):
    def has_permission(self, request, view):
        return request.method in ('GET', 'PATCH', 'DELETE')


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                request.user.role in ('admin', 'superuser')
                or request.user.is_superuser))


class IsAdminOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.role == 'admin')


class IsAuthorOrAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role in ('moderator', 'admin', 'superuser')
            or request.user.is_superuser)
