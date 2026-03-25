"""User and authentication views owned by user_app."""

import secrets
import string
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from dashboard_app.utils.decorators import regular_user_cannot_edit, superuser_only
from dashboard_app.models import Notification
from user_app.forms import UserAccountForm, InitialPasswordChangeForm
from user_app.models import UserPreference
from user_app.utils import get_items_per_page
from user_app.utils import notifications_enabled_for_request


class CustomLoginView(LoginView):
	"""Custom login view that handles remember-me session duration."""

	template_name = 'user_app/accounts/login.html'

	def form_valid(self, form):
		response = super().form_valid(form)
		remember_me = self.request.POST.get('remember_me')

		if remember_me:
			self.request.session.set_expiry(timedelta(days=30))
		else:
			self.request.session.set_expiry(0)

		self.request.session.save()
		return response


def admin_check(user):
	"""Check if user is admin."""
	return user.is_staff and user.is_superuser


@login_required
@user_passes_test(admin_check)
def user_accounts_list(request):
	"""List all user accounts with search and filtering."""
	page_size = get_items_per_page(request)
	all_users = User.objects.all().order_by('-date_joined')
	search_query = request.GET.get('q', '').strip()
	is_searching = bool(search_query)
	status_filter = request.GET.get('status', '')

	if search_query:
		all_users = all_users.filter(
			Q(username__icontains=search_query)
			| Q(email__icontains=search_query)
			| Q(first_name__icontains=search_query)
			| Q(last_name__icontains=search_query)
		)

	if status_filter == 'active':
		all_users = all_users.filter(is_active=True)
	elif status_filter == 'inactive':
		all_users = all_users.filter(is_active=False)
	elif status_filter == 'staff':
		all_users = all_users.filter(is_staff=True)
	elif status_filter == 'superuser':
		all_users = all_users.filter(is_superuser=True)

	total_users = User.objects.count()
	active_users = User.objects.filter(is_active=True).count()
	staff_users = User.objects.filter(is_staff=True).count()
	superusers = User.objects.filter(is_superuser=True).count()

	summary_cards = [
		{
			'label': 'Active Users',
			'value': active_users,
			'description': 'Can login to system',
			'is_currency': False,
			'icon': 'check-circle-fill',
		},
		{
			'label': 'Staff Users',
			'value': staff_users,
			'description': 'Access to admin panel',
			'is_currency': False,
			'icon': 'shield-check',
		},
		{
			'label': 'Superusers',
			'value': superusers,
			'description': 'Complete system access',
			'is_currency': False,
			'icon': 'star-fill',
		},
	]

	if is_searching or status_filter:
		users = all_users
		paginator = None
		page_obj = None
	else:
		paginator = Paginator(all_users, max(page_size, 1))
		page_number = request.GET.get('page', 1)
		users = paginator.get_page(page_number)
		page_obj = users

	user_count = all_users.count()
	toolbar_count = f'{user_count} user{"" if user_count == 1 else "s"}'

	context = {
		'users': users,
		'page_obj': page_obj,
		'paginator': paginator,
		'total_users': total_users,
		'active_users': active_users,
		'staff_users': staff_users,
		'superusers': superusers,
		'summary_cards': summary_cards,
		'search_query': search_query,
		'status_filter': status_filter,
		'is_searching': is_searching,
		'toolbar_count': toolbar_count,
		'filter_options': {
			'active': 'Active Users',
			'inactive': 'Inactive Users',
			'staff': 'Staff Only',
			'superuser': 'Superusers Only',
		},
	}
	return render(request, 'user_app/accounts/user_accounts_list.html', context)


@login_required
@user_passes_test(admin_check)
@superuser_only
@regular_user_cannot_edit
def user_account_create(request):
	"""Create new user account."""
	if request.method == 'POST':
		form = UserAccountForm(request.POST, is_edit=False)
		if form.is_valid():
			user = form.save()
			password = form.cleaned_data.get('password', '').strip()
			if not password and hasattr(user, '_temporary_password'):
				password = user._temporary_password
			return redirect('user_accounts_list')
	else:
		form = UserAccountForm(is_edit=False)

	return render(
		request,
		'user_app/accounts/user_account_form.html',
		{
			'form': form,
			'is_edit': False,
			'title': 'Create New User Account',
		},
	)


@login_required
@user_passes_test(admin_check)
@superuser_only
@regular_user_cannot_edit
def user_account_edit(request, user_id):
	"""Edit existing user account."""
	user = get_object_or_404(User, pk=user_id)

	if user == request.user and request.method == 'POST' and request.POST.get('is_superuser') != 'on':
		messages.error(request, 'You cannot remove your own superuser status!')
		return redirect('user_account_edit', user_id=user_id)

	if request.method == 'POST':
		form = UserAccountForm(request.POST, instance=user, is_edit=True)
		if form.is_valid():
			form.save()
			return redirect('user_accounts_list')
	else:
		form = UserAccountForm(instance=user, is_edit=True)

	return render(
		request,
		'user_app/accounts/user_account_form.html',
		{
			'form': form,
			'user': user,
			'is_edit': True,
			'title': f'Edit User Account - {user.get_full_name() or user.username}',
		},
	)


@login_required
@user_passes_test(admin_check)
def user_account_detail(request, user_id):
	"""View user account details."""
	user = get_object_or_404(User, pk=user_id)
	last_login = user.last_login
	date_joined = user.date_joined
	days_active = (datetime.now(date_joined.tzinfo) - date_joined).days if date_joined else 0
	status = 'Active' if user.is_active else 'Inactive'

	roles = []
	if user.is_superuser:
		roles.append('Superuser (Full permissions)')
	elif user.is_staff:
		roles.append('Staff (Admin access)')
	else:
		roles.append('Regular User')

	return render(
		request,
		'user_app/accounts/user_account_detail.html',
		{
			'viewed_user': user,
			'last_login': last_login,
			'date_joined': date_joined,
			'days_active': days_active,
			'status': status,
			'roles': roles,
		},
	)


@login_required
@user_passes_test(admin_check)
@superuser_only
@require_http_methods(['POST'])
@regular_user_cannot_edit
def user_account_delete(request, user_id):
	"""Delete user account."""
	user = get_object_or_404(User, pk=user_id)

	if user == request.user:
		messages.error(request, 'You cannot delete your own account!')
		return redirect('user_accounts_list')

	username = user.username
	user.delete()
	return redirect('user_accounts_list')


@login_required
@user_passes_test(admin_check)
def user_account_toggle_status(request, user_id):
	"""Toggle user active/inactive status."""
	user = get_object_or_404(User, pk=user_id)

	if user == request.user:
		messages.error(request, 'You cannot disable your own account!')
		return redirect('user_accounts_list')

	user.is_active = not user.is_active
	user.save()
	return redirect('user_accounts_list')


@login_required
@user_passes_test(admin_check)
def user_account_reset_password(request, user_id):
	"""Reset user password and generate new one."""
	user = get_object_or_404(User, pk=user_id)
	new_password = generate_secure_password()
	user.set_password(new_password)
	user.save()
	return redirect('user_accounts_list')


def generate_secure_password(length=12):
	"""Generate a secure random password."""
	alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
	return ''.join(secrets.choice(alphabet) for _ in range(length))


@login_required
@user_passes_test(admin_check)
def api_user_accounts_data(request):
	"""API endpoint for user accounts data (for AJAX/charts)."""
	users = User.objects.all()
	data = {
		'total_users': users.count(),
		'active_users': users.filter(is_active=True).count(),
		'inactive_users': users.filter(is_active=False).count(),
		'staff_users': users.filter(is_staff=True).count(),
		'superusers': users.filter(is_superuser=True).count(),
		'regular_users': users.filter(is_staff=False).count(),
		'last_7_days': users.filter(date_joined__gte=datetime.now() - timedelta(days=7)).count(),
	}
	return JsonResponse(data)


@login_required
def change_initial_password(request):
	"""Force user to change initial password on first login."""
	user = request.user

	try:
		pref = UserPreference.objects.get(user=user)
		if pref.password_changed:
			return redirect('dashboard')
	except UserPreference.DoesNotExist:
		UserPreference.objects.create(user=user, password_changed=False)

	if request.method == 'POST':
		form = InitialPasswordChangeForm(user, request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, user)
			return redirect('dashboard')
	else:
		form = InitialPasswordChangeForm(user)

	return render(
		request,
		'user_app/accounts/change_password.html',
		{
			'form': form,
			'force_change': True,
			'username': user.username,
		},
	)


@login_required
def user_settings(request):
	"""User settings and preferences page."""
	preference, _ = UserPreference.objects.get_or_create(user=request.user)

	if request.method == 'POST':
		theme = request.POST.get('theme', 'dark')
		notifications = request.POST.get('notifications_enabled', False) == 'on'
		items_per_page = request.POST.get('items_per_page', 25)

		if theme not in ['dark', 'light']:
			theme = 'dark'

		preference.theme = theme
		preference.notifications_enabled = notifications
		preference.items_per_page = int(items_per_page) if items_per_page.isdigit() else 25
		preference.save()
		return redirect('user_settings')

	return render(
		request,
		'user_app/settings.html',
		{
			'preference': preference,
			'theme_choices': [('dark', 'Dark Theme'), ('light', 'Light Theme')],
			'page_size_options': [10, 25, 50, 100],
		},
	)


@login_required
def api_update_theme(request):
	"""API endpoint to update theme via AJAX."""
	if request.method == 'POST':
		theme = request.POST.get('theme', 'dark')
		if theme not in ['dark', 'light']:
			return JsonResponse({'success': False, 'error': 'Invalid theme'})

		preference, _ = UserPreference.objects.get_or_create(user=request.user)
		preference.theme = theme
		preference.save()

		return JsonResponse({'success': True, 'theme': theme, 'message': 'Theme updated successfully'})

	return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def api_change_password(request):
	"""AJAX endpoint to change password."""
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)

		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			return JsonResponse({'success': True, 'message': 'Password changed successfully!'})

		errors = {}
		for field, field_errors in form.errors.items():
			errors[field] = [str(e) for e in field_errors]

		return JsonResponse({'success': False, 'errors': errors, 'message': 'Please fix the errors below'})

	return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
@require_GET
def api_notifications(request):
	"""Return latest notifications and unread count for the current user."""
	if not notifications_enabled_for_request(request):
		return JsonResponse({'notifications': [], 'unread_count': 0})

	try:
		notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
		unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
	except (ProgrammingError, OperationalError):
		return JsonResponse({'notifications': [], 'unread_count': 0})

	payload = [
		{
			'id': notif.id,
			'title': notif.title,
			'message': notif.message,
			'level': notif.level,
			'category': notif.category,
			'is_read': notif.is_read,
			'created_at': notif.created_at.isoformat(),
			'created_display': notif.created_at.strftime('%b %d, %Y %I:%M %p'),
		}
		for notif in notifications
	]

	return JsonResponse({'notifications': payload, 'unread_count': unread_count})


@login_required
@require_POST
def api_notification_mark_read(request, notification_id):
	"""Mark a single notification as read."""
	try:
		notif = Notification.objects.filter(user=request.user, pk=notification_id).first()
	except (ProgrammingError, OperationalError):
		return JsonResponse({'success': True, 'unread_count': 0})

	if not notif:
		return JsonResponse({'success': False, 'message': 'Notification not found'}, status=404)

	notif.mark_as_read()
	unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
	return JsonResponse({'success': True, 'unread_count': unread_count})


@login_required
@require_POST
def api_notifications_mark_all_read(request):
	"""Mark all notifications as read for current user."""
	try:
		notifications = Notification.objects.filter(user=request.user, is_read=False)
	except (ProgrammingError, OperationalError):
		return JsonResponse({'success': True, 'unread_count': 0})

	for notif in notifications:
		notif.mark_as_read()

	return JsonResponse({'success': True, 'unread_count': 0})


__all__ = [
	'CustomLoginView',
	'user_accounts_list',
	'user_account_create',
	'user_account_edit',
	'user_account_detail',
	'user_account_delete',
	'user_account_toggle_status',
	'user_account_reset_password',
	'api_user_accounts_data',
	'change_initial_password',
	'user_settings',
	'api_update_theme',
	'api_change_password',
	'api_notifications',
	'api_notifications_mark_all_read',
	'api_notification_mark_read',
]
