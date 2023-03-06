from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and (
                request.user.role in ('admin', 'superuser')
                or request.user.is_superuser))


class DeleteGetPatchPermission(BaseException):
    def has_permission(self, request, view):
        return request.method in ('GET', 'PATCH', 'DELETE')
