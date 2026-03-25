"""
Custom decorators for permission-based access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def regular_user_cannot_edit(view_func):
    """
    Decorator that restricts regular users (non-staff, non-superuser) from 
    accessing create, edit, and delete views.
    
    Only staff and superusers can access these functions.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow staff and superusers
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Deny regular users
        messages.error(
            request, 
            "You do not have permission to perform this action. "
            "Only staff members can create, edit, or delete records."
        )
        return redirect('dashboard')
    
    return wrapper


def superuser_only(view_func):
    """
    Decorator that restricts access to superusers only.
    
    Only superusers can access these functions. Staff users are denied.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow only superusers
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Deny staff and regular users
        messages.error(
            request, 
            "You do not have permission to perform this action. "
            "Only system administrators can access this feature."
        )
        return redirect('dashboard')
    
    return wrapper
