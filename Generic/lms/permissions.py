# permissions.py
from rest_framework import permissions

class IsCourseOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow course owners to edit/delete it.
    """
    message = "You must be the owner of this course to perform this action."
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the course
        return obj.owner == request.user
    
    

class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow users with 'Student' role to access the view.
    """
    message = "Only users with Student role can access this endpoint."

    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'Student' role
        return bool(
            request.user and 
            request.user.is_authenticated and
            request.user.role == 'Student'
        )