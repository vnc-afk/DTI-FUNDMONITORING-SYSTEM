"""
User Settings and Preferences Views
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from user_app.models import UserPreference


@login_required
def user_settings(request):
    """User settings and preferences page"""
    # Get or create user preference
    preference, created = UserPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update theme preference
        theme = request.POST.get('theme', 'dark')
        notifications = request.POST.get('notifications_enabled', False) == 'on'
        items_per_page = request.POST.get('items_per_page', 25)
        
        # Validate theme
        if theme not in ['dark', 'light']:
            theme = 'dark'
        
        # Update preferences
        preference.theme = theme
        preference.notifications_enabled = notifications
        preference.items_per_page = int(items_per_page) if items_per_page.isdigit() else 25
        preference.save()
        
        return redirect('user_settings')
    
    context = {
        'preference': preference,
        'theme_choices': [('dark', 'Dark Theme'), ('light', 'Light Theme')],
        'page_size_options': [10, 25, 50, 100],
    }
    
    return render(request, 'settings.html', context)


@login_required
def api_update_theme(request):
    """API endpoint to update theme via AJAX"""
    if request.method == 'POST':
        theme = request.POST.get('theme', 'dark')
        
        # Validate theme
        if theme not in ['dark', 'light']:
            return JsonResponse({'success': False, 'error': 'Invalid theme'})
        
        # Get or create preference
        preference, _ = UserPreference.objects.get_or_create(user=request.user)
        preference.theme = theme
        preference.save()
        
        return JsonResponse({
            'success': True,
            'theme': theme,
            'message': 'Theme updated successfully'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def api_change_password(request):
    """AJAX endpoint to change password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Password changed successfully!'
            })
        else:
            # Collect all form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(e) for e in field_errors]
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please fix the errors below'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
