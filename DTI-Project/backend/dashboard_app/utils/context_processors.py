"""Context processors for shared dashboard template data."""

from django.db.utils import OperationalError, ProgrammingError

from dashboard_app.models import Notification
from user_app.utils import notifications_enabled_for_request


def get_page_title(url_name):
    """Map URL resolver names to human-readable page titles."""
    title_map = {
        "dashboard": "Financial Dashboard",
        "executive_dashboard": "Executive Dashboard",
        "master_fund_monitoring_list": "Master Fund Monitoring",
        "master_fund_monitoring_add": "Add Fund Monitoring",
        "master_fund_monitoring_edit": "Edit Fund Monitoring",
        "bank_statement_list": "Bank Statement",
        "bank_statement_add": "Add Bank Statement",
        "bank_statement_edit": "Edit Bank Statement",
        "activity_logs": "Activity Logs",
        "activity_summary": "Activity Summary",
        "model_activity_logs": "Activity",
        "user_activity_logs": "User Activity Logs",
        "archived_dashboard": "Archive Management",
        "archived_transactions": "Archived Transactions",
        "archived_statements": "Archived Statements",
        "import_data": "Import Data",
        "import_result": "Import Results",
        "supplier_list": "Supplier List",
        "supplier_add": "Add Supplier",
        "supplier_edit": "Edit Supplier",
        "fund_source_list": "Fund Sources",
        "fund_source_add": "Add Fund Source",
        "fund_source_edit": "Edit Fund Source",
        "fund_source_breakdowns": "Breakdown",
        "expense_object_list": "Expense Object List",
        "expense_object_add": "Add Expense Object",
        "expense_object_edit": "Edit Expense Object",
        "expense_category_list": "Expense Category List",
        "expense_category_add": "Add Expense Category",
        "expense_category_edit": "Edit Expense Category",
        "staff_list": "Staff List",
        "staff_add": "Add Staff",
        "staff_edit": "Edit Staff",
        "tax_table": "Tax Table",
        "tax_add": "Add Tax Entry",
        "tax_edit": "Edit Tax Entry",
        "user_settings": "Settings & Preferences",
        "user_accounts_list": "User Accounts",
        "user_account_detail": "User Details",
        "fund_report": "Fund Report",
        "mooe_report": "MOOE Report",
        "expenses_report": "Expenses",
        "negosyo_center_report": "Negosyo Center Report",
        "tin_report": "TIN Report",
    }
    return title_map.get(url_name, "Dashboard")


def page_title(request):
    """Inject page_title into template context based on current view."""
    try:
        # Try to get the URL resolver name
        url_name = request.resolver_match.url_name if request.resolver_match else None
        title = get_page_title(url_name) if url_name else "Dashboard"
    except (AttributeError, TypeError):
        title = "Dashboard"

    return {"page_title": title}


def topbar_notifications(request):
    """Inject unread count and latest notifications for the topbar bell dropdown."""
    if not request.user.is_authenticated:
        return {
            "topbar_notifications": [],
            "topbar_unread_notification_count": 0,
        }

    if not notifications_enabled_for_request(request):
        return {
            "topbar_notifications": [],
            "topbar_unread_notification_count": 0,
        }

    try:
        notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )[:8]
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    except (ProgrammingError, OperationalError):
        # Notification table may not exist yet if migrations are pending.
        return {
            "topbar_notifications": [],
            "topbar_unread_notification_count": 0,
        }

    return {
        "topbar_notifications": notifications,
        "topbar_unread_notification_count": unread_count,
    }
