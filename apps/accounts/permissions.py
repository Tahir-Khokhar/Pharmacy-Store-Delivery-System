from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework import permissions
from .models import UserRole

def role_required(allowed_roles):
    """
    Decorator for views that checks if the logged-in user belongs to one of allowed roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect('accounts:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("You do not have permission to access this pharmacy area.")
        return _wrapped_view
    return decorator

pharmacist_required = role_required([UserRole.PHARMACIST, UserRole.ADMIN])
inventory_manager_required = role_required([UserRole.INVENTORY_MANAGER, UserRole.ADMIN])
delivery_staff_required = role_required([UserRole.DELIVERY_STAFF, UserRole.ADMIN])
admin_required = role_required([UserRole.ADMIN])


# DRF Permissions
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.CUSTOMER)


class IsPharmacist(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == UserRole.PHARMACIST or request.user.is_superuser))


class IsInventoryManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == UserRole.INVENTORY_MANAGER or request.user.is_superuser))


class IsDeliveryStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == UserRole.DELIVERY_STAFF or request.user.is_superuser))


class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == UserRole.ADMIN or request.user.is_superuser or request.user.is_staff))


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role in [UserRole.ADMIN, UserRole.PHARMACIST]:
            return True
        user_field = getattr(obj, 'user', getattr(obj, 'customer', None))
        return user_field == request.user
