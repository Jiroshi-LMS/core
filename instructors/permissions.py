from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        field = obj.owner_field
        return getattr(obj, field) == request.user
    

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)