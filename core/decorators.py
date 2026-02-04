from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def financial_access_required(view_func):
    """
    Decorator to restrict access to financial features only to authorized roles
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role in ['super_admin', 'accountant']:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You don't have permission to access financial features.")
    return wrapper

def accountant_or_admin_required(view_func):
    """
    Decorator specifically for accountant and admin access
    """
    return financial_access_required(view_func)
