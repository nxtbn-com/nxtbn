from rest_framework.permissions import BasePermission

class NxtbnAdminPermission(BasePermission):
    """
    Custom permission class that checks if a user has the required permission 
    to perform an action on a specific model, based on Django Admin model-level permissions.
    """

    def has_permission(self, request, view):
        # Ensure the user is a staff member and is active
        if not request.user.is_staff or not request.user.is_active:
            return False
        
        # Superusers always have full access
        if request.user.is_superuser:
            return True
        
        # Get the model associated with the view's queryset
        model = getattr(view.queryset, 'model', None)

        if model is None:
            return False  # Cannot proceed without a model reference

        # Mapping of HTTP methods to Django permission actions
        action_permissions = {
            'get': 'view',
            'post': 'add',
            'put': 'change',
            'patch': 'change',
            'delete': 'delete'
        }

        # Determine the required permission for the HTTP method
        permission_action = action_permissions.get(request.method.lower(), None)

        if permission_action is None:
            return False  # Unsupported HTTP method
        
        # Build the permission codename (e.g., 'add_modelname')
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        permission_codename = f"{permission_action}_{model_name}"

        # Check if the user has the specific permission
        return request.user.has_perm(f"{app_label}.{permission_codename}")



class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
