"""Notification API views for topbar alert interactions."""

from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from dashboard_app.models import Notification
from user_app.utils import notifications_enabled_for_request


@login_required
@require_GET
def api_notifications(request):
    """Return latest notifications and unread count for the current user."""
    if not notifications_enabled_for_request(request):
        return JsonResponse({"notifications": [], "unread_count": 0})

    try:
        notifications = Notification.objects.filter(user=request.user).order_by("-created_at")[:10]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    except (ProgrammingError, OperationalError):
        return JsonResponse({"notifications": [], "unread_count": 0})

    payload = [
        {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "level": notif.level,
            "category": notif.category,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat(),
            "created_display": notif.created_at.strftime("%b %d, %Y %I:%M %p"),
        }
        for notif in notifications
    ]

    return JsonResponse({"notifications": payload, "unread_count": unread_count})


@login_required
@require_POST
def api_notification_mark_read(request, notification_id):
    """Mark a single notification as read."""
    try:
        notif = Notification.objects.filter(user=request.user, pk=notification_id).first()
    except (ProgrammingError, OperationalError):
        return JsonResponse({"success": True, "unread_count": 0})

    if not notif:
        return JsonResponse({"success": False, "message": "Notification not found"}, status=404)

    notif.mark_as_read()

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"success": True, "unread_count": unread_count})


@login_required
@require_POST
def api_notifications_mark_all_read(request):
    """Mark all notifications as read for current user."""
    try:
        notifications = Notification.objects.filter(user=request.user, is_read=False)
    except (ProgrammingError, OperationalError):
        return JsonResponse({"success": True, "unread_count": 0})

    for notif in notifications:
        notif.mark_as_read()

    return JsonResponse({"success": True, "unread_count": 0})
