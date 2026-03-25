from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from dashboard_app.models import ActivityLog
from django.utils.timezone import now, timedelta
from user_app.utils import get_items_per_page


@login_required
def activity_logs(request):
    """
    Display activity logs with filtering and pagination
    Only superusers can access this view
    """
    # Restrict to superusers only
    if not request.user.is_superuser:
        return render(request, '403.html', status=403)
    
    logs = ActivityLog.objects.all()
    page_size = get_items_per_page(request)
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    model_filter = request.GET.get('model', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        try:
            logs = logs.filter(user_id=int(user_filter))
        except (ValueError, TypeError):
            pass
    
    if model_filter:
        logs = logs.filter(model_name=model_filter)
    
    if date_filter:
        if date_filter == 'today':
            logs = logs.filter(timestamp__date=now().date())
        elif date_filter == 'week':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=7))
        elif date_filter == 'month':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=30))
    
    if search_query:
        logs = logs.filter(
            Q(object_repr__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(logs, max(page_size, 1))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for dropdowns
    actions = ActivityLog.ACTION_CHOICES
    users = User.objects.filter(activity_logs__isnull=False).distinct().order_by('username')
    models = ActivityLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
    
    context = {
        'logs': page_obj,
        'paginator': paginator,
        'actions': actions,
        'users': users,
        'models': models,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'model_filter': model_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'total_logs': logs.count(),
    }
    
    return render(request, 'dashboard_app/activity_logs/activity_logs.html', context)


@login_required
def user_activity_logs(request, user_id):
    """
    Display activity logs for a specific user
    """
    # Check permissions - users can only view their own logs unless admin
    if request.user.id != user_id and not request.user.is_staff:
        return render(request, '403.html', status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, '404.html', status=404)
    
    logs = ActivityLog.objects.filter(user=user)
    page_size = get_items_per_page(request)
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if date_filter:
        if date_filter == 'today':
            logs = logs.filter(timestamp__date=now().date())
        elif date_filter == 'week':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=7))
        elif date_filter == 'month':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=30))
    
    if search_query:
        logs = logs.filter(
            Q(object_repr__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(logs, max(page_size, 1))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    actions = ActivityLog.ACTION_CHOICES
    
    context = {
        'logs': page_obj,
        'paginator': paginator,
        'viewed_user': user,
        'actions': actions,
        'action_filter': action_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'total_logs': logs.count(),
    }
    
    return render(request, 'dashboard_app/activity_logs/user_activity_logs.html', context)


@login_required
def model_activity_logs(request, model_name):
    """
    Display activity logs for a specific model
    Only superusers can access this view
    """
    # Restrict to superusers only
    if not request.user.is_superuser:
        return render(request, '403.html', status=403)
    
    logs = ActivityLog.objects.filter(model_name=model_name)
    page_size = get_items_per_page(request)
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        try:
            logs = logs.filter(user_id=int(user_filter))
        except (ValueError, TypeError):
            pass
    
    if date_filter:
        if date_filter == 'today':
            logs = logs.filter(timestamp__date=now().date())
        elif date_filter == 'week':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=7))
        elif date_filter == 'month':
            logs = logs.filter(timestamp__gte=now() - timedelta(days=30))
    
    if search_query:
        logs = logs.filter(
            Q(object_repr__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(logs, max(page_size, 1))
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    actions = ActivityLog.ACTION_CHOICES
    users = User.objects.filter(activity_logs__model_name=model_name).distinct().order_by('username')
    
    context = {
        'logs': page_obj,
        'paginator': paginator,
        'model_name': model_name,
        'actions': actions,
        'users': users,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'total_logs': logs.count(),
    }
    
    return render(request, 'dashboard_app/activity_logs/model_activity_logs.html', context)


@login_required
def activity_summary(request):
    """
    Display activity summary and statistics
    Only superusers can access this view
    """
    # Only superusers can view summary
    if not request.user.is_superuser:
        return render(request, '403.html', status=403)
    
    now_time = now()
    today = now_time.date()
    
    # Calculate statistics
    total_logs = ActivityLog.objects.count()
    today_logs = ActivityLog.objects.filter(timestamp__date=today).count()
    week_logs = ActivityLog.objects.filter(timestamp__gte=now_time - timedelta(days=7)).count()
    month_logs = ActivityLog.objects.filter(timestamp__gte=now_time - timedelta(days=30)).count()
    
    # Actions breakdown
    actions_breakdown = ActivityLog.objects.values('action').annotate(
        count=__import__('django.db.models', fromlist=['Count']).Count('id')
    ).order_by('-count')
    
    # Most active users
    active_users = ActivityLog.objects.values('user__username', 'user__first_name', 'user__last_name').annotate(
        count=__import__('django.db.models', fromlist=['Count']).Count('id')
    ).order_by('-count')[:10]
    
    # Most modified models
    modified_models = ActivityLog.objects.values('model_name').annotate(
        count=__import__('django.db.models', fromlist=['Count']).Count('id')
    ).order_by('-count')[:10]
    
    # Recent sensitive activities
    sensitive_logs = ActivityLog.objects.filter(is_sensitive=True).order_by('-timestamp')[:10]
    
    context = {
        'total_logs': total_logs,
        'today_logs': today_logs,
        'week_logs': week_logs,
        'month_logs': month_logs,
        'actions_breakdown': actions_breakdown,
        'active_users': active_users,
        'modified_models': modified_models,
        'sensitive_logs': sensitive_logs,
    }
    
    return render(request, 'dashboard_app/activity_logs/activity_summary.html', context)
