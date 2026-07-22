from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    """Usage: permission_classes = [IsRole('provider', 'admin')]"""

    def __init__(self, *roles):
        self.roles = roles

    def __call__(self):
        return self

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False) and user.role in self.roles)


class IsAuthenticatedStateless(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False))
