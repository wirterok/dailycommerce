from rest_framework.permissions import BasePermission, SAFE_METHODS
from db.core import PermissionsTypes
from .utils import get_user_permission

CHANGE_METHODS = ["POST", "DELETE", "PATCH", "PUT"]
READ_ALL = [PermissionsTypes.NONE, PermissionsTypes.ADMIN, PermissionsTypes.READ_ONLY]


class CustomPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method in CHANGE_METHODS:
            permission = get_user_permission(request, view)
            if not permission:
                return True

            if permission.rights != PermissionsTypes.READ_ONLY:
                return True
        
        return False


    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            permission = get_user_permission(request, view)
            if not permission:
                return True
            if permission.rights in READ_ALL:
                return True
            if permission.rights == PermissionsTypes.CREATOR:
                if request.user.id == obj.user_owner:
                    return True
            return False

        if request.method in CHANGE_METHODS:
            permission = get_user_permission(request, view)
            if not permission:
                return True
            if permission.rights in [PermissionsTypes.NONE, PermissionsTypes.ADMIN]:
                return True
            if permission.rights == PermissionsTypes.CREATOR:
                if request.user.id == obj.user_owner:
                    return True               
            return False       
        
        return False




