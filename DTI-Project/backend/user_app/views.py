"""User API views owned by user_app."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from dashboard_app.models import Notification
from dashboard_app.utils.decorators import api_login_required
from user_app.forms import InitialPasswordChangeForm
from user_app.models import UserPreference
from user_app.utils import get_items_per_page, notifications_enabled_for_request


class CustomLoginView(LoginView):
    """Session-based login view for the web interface."""

    template_name = "user_app/accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        remember_me = self.request.POST.get("remember_me")
        if remember_me:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)

        # Ensure preference row exists for middleware checks.
        UserPreference.objects.get_or_create(user=self.request.user)
        return response

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return reverse("admin:index")


@login_required
def change_initial_password(request):
    """Force user to change temporary password on first login."""
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    force_change = not preference.password_changed

    if request.method == "POST":
        form = InitialPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed successfully.")
            return redirect(reverse("admin:index"))
    else:
        form = InitialPasswordChangeForm(request.user)

    return render(
        request,
        "user_app/accounts/change_password.html",
        {
            "form": form,
            "force_change": force_change,
        },
    )


@api_login_required
@require_POST
def api_change_password(request):
    """AJAX endpoint to change password."""
    form = PasswordChangeForm(request.user, request.POST)

    if form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        return JsonResponse(
            {"success": True, "message": "Password changed successfully!"}
        )

    errors = {
        field: [str(err) for err in field_errors]
        for field, field_errors in form.errors.items()
    }
    return JsonResponse(
        {"success": False, "errors": errors, "message": "Please fix the errors below"}
    )


@api_login_required
@require_GET
def api_notifications(request):
    """Return latest notifications and unread count for the current user."""
    if not notifications_enabled_for_request(request):
        return JsonResponse({"notifications": [], "unread_count": 0})

    requested_limit = request.GET.get("limit")
    if requested_limit is not None:
        try:
            limit = int(requested_limit)
        except (TypeError, ValueError):
            limit = 10
    else:
        limit = get_items_per_page(request, default=10)

    limit = max(1, min(limit, 100))

    try:
        notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )[:limit]
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
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


@api_login_required
@csrf_exempt
@require_POST
def api_notification_mark_read(request, notification_id):
    """Mark a single notification as read."""
    try:
        notif = Notification.objects.filter(
            user=request.user, pk=notification_id
        ).first()
    except (ProgrammingError, OperationalError):
        return JsonResponse({"success": True, "unread_count": 0})

    if not notif:
        return JsonResponse(
            {"success": False, "message": "Notification not found"}, status=404
        )

    notif.mark_as_read()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"success": True, "unread_count": unread_count})


@api_login_required
@csrf_exempt
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


__all__ = [
    "CustomLoginView",
    "change_initial_password",
    "api_change_password",
    "api_notifications",
    "api_notifications_mark_all_read",
    "api_notification_mark_read",
]
