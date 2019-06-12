from rest_framework.permissions import BasePermission

class AuthLevel2Permission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.auth_level < 2:
            return False
        else:
            return True
