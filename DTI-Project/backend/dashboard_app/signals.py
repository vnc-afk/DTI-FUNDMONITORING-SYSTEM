"""
Django signals for dashboard_app
Handles automatic sync between BankStatement and MasterFundMonitoring
Also handles activity logging for all model changes
"""

from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.db.utils import OperationalError, ProgrammingError
from django.dispatch import receiver
from django.utils import timezone

from bank_statement_app.models import BankStatement
from data_management_app.models import (
    FundSource,
    FundSourceBreakdown,
    PurchaseType,
    Staff,
    Supplier,
    TaxTable,
)
from mater_fundmonitor_app.models import MasterFundMonitoring
from user_app.utils import notifications_enabled_for_user

from .middleware import get_current_user
from .models import ActivityLog, Notification
from .realtime import broadcast_to_roles, broadcast_to_user

# ════════════════════════════════════════════════════════════════════════════
# SYNC SIGNALS
# ════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════════════════
# ACTIVITY LOGGING SIGNALS
# ════════════════════════════════════════════════════════════════════════════


def log_activity(user, action, model_name, object_id, object_repr, description=""):
    """Helper function to create activity log entries"""
    if user and user.is_authenticated:
        ActivityLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            description=description,
        )

        broadcast_to_roles(
            event_type="live.update",
            payload={
                "model_name": model_name,
                "action": action,
                "object_id": object_id,
                "object_repr": object_repr,
                "description": description,
                "actor_id": user.id,
                "actor_name": user.get_full_name() or user.username,
            },
        )


def create_notifications_for_active_users(
    title, message, *, level, category, actor=None, event_key=None
):
    """Create the same notification for all active users, with optional deduplication."""
    try:
        active_users = User.objects.filter(is_active=True)
        for user in active_users:
            if not notifications_enabled_for_user(user):
                continue

            if event_key:
                duplicate_exists = Notification.objects.filter(
                    user=user,
                    event_key=event_key,
                    is_read=False,
                ).exists()
                if duplicate_exists:
                    continue

            Notification.objects.create(
                user=user,
                actor=actor,
                title=title,
                message=message,
                level=level,
                category=category,
                event_key=event_key,
            )
    except (ProgrammingError, OperationalError):
        # Ignore during rollout when notification migration has not run yet.
        return


def evaluate_budget_threshold_alerts(fund_source, actor=None):
    """Generate budget risk alerts when usage reaches warning or critical thresholds."""
    if not fund_source or not fund_source.annual_budget:
        return

    total_spent = (
        MasterFundMonitoring.objects.filter(
            fund_source=fund_source,
            transaction_type="Disbursement",
        ).aggregate(total=Sum("payments"))["total"]
        or 0
    )

    if fund_source.annual_budget <= 0:
        return

    usage_ratio = float(total_spent / fund_source.annual_budget)

    if usage_ratio >= 1.0:
        percentage = round(usage_ratio * 100, 1)
        create_notifications_for_active_users(
            title="Fund/Budget notification",
            message=(
                f"{fund_source.name} has reached {percentage}% utilization "
                f"(spent: {total_spent:,.2f} / budget: {fund_source.annual_budget:,.2f})."
            ),
            level=Notification.LEVEL_CRITICAL,
            category=Notification.CATEGORY_FUND_BUDGET,
            actor=actor,
            event_key=f"budget-critical-{fund_source.id}",
        )
    elif usage_ratio >= 0.8:
        percentage = round(usage_ratio * 100, 1)
        create_notifications_for_active_users(
            title="Fund/Budget notification",
            message=(
                f"{fund_source.name} is at {percentage}% utilization "
                f"(spent: {total_spent:,.2f} / budget: {fund_source.annual_budget:,.2f})."
            ),
            level=Notification.LEVEL_WARNING,
            category=Notification.CATEGORY_FUND_BUDGET,
            actor=actor,
            event_key=f"budget-warning-{fund_source.id}",
        )


def create_financial_analysis_notification(fund_source, actor=None):
    """Create daily financial analysis snapshot notifications per fund source."""
    if (
        not fund_source
        or not fund_source.annual_budget
        or fund_source.annual_budget <= 0
    ):
        return

    total_spent = (
        MasterFundMonitoring.objects.filter(
            fund_source=fund_source,
            transaction_type="Disbursement",
        ).aggregate(total=Sum("payments"))["total"]
        or 0
    )

    remaining_budget = fund_source.annual_budget - total_spent
    utilization = float(total_spent / fund_source.annual_budget) * 100
    level = Notification.LEVEL_WARNING if utilization >= 80 else Notification.LEVEL_INFO

    create_notifications_for_active_users(
        title="Financial analysis notification",
        message=(
            f"{fund_source.name} analysis: utilization {utilization:.1f}%, "
            f"spent {total_spent:,.2f}, remaining {remaining_budget:,.2f}."
        ),
        level=level,
        category=Notification.CATEGORY_FINANCIAL_ANALYSIS,
        actor=actor,
        event_key=f"financial-analysis-{fund_source.id}-{timezone.localdate().isoformat()}",
    )


# BankStatement Activity Logging
@receiver(post_save, sender=BankStatement)
def log_bankstatement_activity(sender, instance, created, **kwargs):
    """Log BankStatement CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        object_repr = f"Transaction {instance.id} - {instance.date}"
        # Calculate transaction amount (debit or credit)
        amount = instance.debit if instance.debit else instance.credit
        description = f"Transaction: {instance.description}, Amount: {amount}"

        log_activity(
            user, action, "BankStatement", instance.id, object_repr, description
        )

        if created:
            create_notifications_for_active_users(
                title="Finance monitoring notification",
                message=(
                    f"A bank transaction was posted ({instance.description}) with "
                    f"balance {instance.balance:,.2f}."
                ),
                level=Notification.LEVEL_INFO,
                category=Notification.CATEGORY_FINANCE_MONITORING,
                actor=user,
                event_key=f"finance-monitor-bank-create-{instance.id}",
            )

        if instance.balance is not None and instance.balance < 0:
            create_notifications_for_active_users(
                title="Finance monitoring notification",
                message=(
                    f"Bank statement transaction {instance.id} created a negative balance "
                    f"of {instance.balance:,.2f}."
                ),
                level=Notification.LEVEL_CRITICAL,
                category=Notification.CATEGORY_FINANCE_MONITORING,
                actor=user,
                event_key=f"negative-balance-{instance.id}",
            )


@receiver(post_delete, sender=BankStatement)
def log_bankstatement_delete(sender, instance, **kwargs):
    """Log BankStatement DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        object_repr = f"Transaction {instance.id} - {instance.date}"
        # Calculate transaction amount (debit or credit)
        amount = instance.debit if instance.debit else instance.credit
        description = f"Deleted transaction: {instance.description}, Amount: {amount}"
        log_activity(
            user, "DELETE", "BankStatement", instance.id, object_repr, description
        )


# MasterFundMonitoring Activity Logging
@receiver(post_save, sender=MasterFundMonitoring)
def log_masterfundmonitoring_activity(sender, instance, created, **kwargs):
    """Log MasterFundMonitoring CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        object_repr = f"Fund Monitor {instance.id}"
        # Get fund source name if available
        fund_name = str(instance.fund_source) if instance.fund_source else "Unknown"
        # Get payment amount
        amount = instance.payments if instance.payments else 0
        description = f"Fund: {fund_name}, Amount: {amount}"

        log_activity(
            user, action, "MasterFundMonitoring", instance.id, object_repr, description
        )

        if created:
            create_notifications_for_active_users(
                title="Finance notification",
                message=(
                    f"A finance entry was recorded under {fund_name} with amount {amount:,.2f}."
                ),
                level=Notification.LEVEL_SUCCESS,
                category=Notification.CATEGORY_FINANCE,
                actor=user,
                event_key=f"finance-create-{instance.id}",
            )
        else:
            create_notifications_for_active_users(
                title="Finance monitoring notification",
                message=(
                    f"Finance record #{instance.id} under {fund_name} was updated."
                ),
                level=Notification.LEVEL_INFO,
                category=Notification.CATEGORY_FINANCE_MONITORING,
                actor=user,
                event_key=f"finance-update-{instance.id}-{timezone.localdate().isoformat()}",
            )

        create_financial_analysis_notification(instance.fund_source, actor=user)
        evaluate_budget_threshold_alerts(instance.fund_source, actor=user)


@receiver(post_delete, sender=MasterFundMonitoring)
def log_masterfundmonitoring_delete(sender, instance, **kwargs):
    """Log MasterFundMonitoring DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        object_repr = f"Fund Monitor {instance.id}"
        log_activity(user, "DELETE", "MasterFundMonitoring", instance.id, object_repr)


# Supplier Activity Logging
@receiver(post_save, sender=Supplier)
def log_supplier_activity(sender, instance, created, **kwargs):
    """Log Supplier CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        object_repr = instance.supplier

        log_activity(user, action, "Supplier", instance.id, object_repr)


@receiver(post_delete, sender=Supplier)
def log_supplier_delete(sender, instance, **kwargs):
    """Log Supplier DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        object_repr = instance.supplier
        log_activity(user, "DELETE", "Supplier", instance.id, object_repr)


# Staff Activity Logging
@receiver(post_save, sender=Staff)
def log_staff_activity(sender, instance, created, **kwargs):
    """Log Staff CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        object_repr = full_name or instance.first_name

        log_activity(user, action, "Staff", instance.id, object_repr)


@receiver(post_delete, sender=Staff)
def log_staff_delete(sender, instance, **kwargs):
    """Log Staff DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        object_repr = full_name or instance.first_name
        log_activity(user, "DELETE", "Staff", instance.id, object_repr)


# FundSource Activity Logging
@receiver(post_save, sender=FundSource)
def log_fundsource_activity(sender, instance, created, **kwargs):
    """Log FundSource CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        object_repr = instance.name
        description = f"Fund Source Budget: {instance.annual_budget}"

        log_activity(user, action, "FundSource", instance.id, object_repr, description)

        create_notifications_for_active_users(
            title="Fund/Budget notification",
            message=(
                f"Fund source {instance.name} was {'created' if created else 'updated'} "
                f"with annual budget {instance.annual_budget:,.2f}."
            ),
            level=Notification.LEVEL_SUCCESS if created else Notification.LEVEL_INFO,
            category=Notification.CATEGORY_FUND_BUDGET,
            actor=user,
            event_key=(
                f"fund-budget-create-{instance.id}"
                if created
                else f"fund-budget-update-{instance.id}-{timezone.localdate().isoformat()}"
            ),
        )

        create_financial_analysis_notification(instance, actor=user)
        evaluate_budget_threshold_alerts(instance, actor=user)


@receiver(post_delete, sender=FundSource)
def log_fundsource_delete(sender, instance, **kwargs):
    """Log FundSource DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        object_repr = instance.name
        log_activity(user, "DELETE", "FundSource", instance.id, object_repr)


# FundSourceBreakdown Activity Logging
@receiver(post_save, sender=FundSourceBreakdown)
def log_fundsourcebreakdown_activity(sender, instance, created, **kwargs):
    """Log FundSourceBreakdown CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        fund_name = str(instance.fund_source) if instance.fund_source else "Unknown"
        object_repr = f"Breakdown: {fund_name}"
        description = f"Budget Amount: {instance.budget_amount}"

        log_activity(
            user, action, "FundSourceBreakdown", instance.id, object_repr, description
        )

        create_notifications_for_active_users(
            title="Fund/Budget notification",
            message=(
                f"Budget breakdown for {fund_name} was {'added' if created else 'updated'} "
                f"with amount {instance.budget_amount:,.2f}."
            ),
            level=Notification.LEVEL_INFO,
            category=Notification.CATEGORY_FUND_BUDGET,
            actor=user,
            event_key=(
                f"fund-breakdown-create-{instance.id}"
                if created
                else f"fund-breakdown-update-{instance.id}-{timezone.localdate().isoformat()}"
            ),
        )


@receiver(post_delete, sender=FundSourceBreakdown)
def log_fundsourcebreakdown_delete(sender, instance, **kwargs):
    """Log FundSourceBreakdown DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        fund_name = str(instance.fund_source) if instance.fund_source else "Unknown"
        object_repr = f"Breakdown: {fund_name}"
        log_activity(user, "DELETE", "FundSourceBreakdown", instance.id, object_repr)


# PurchaseType Activity Logging
@receiver(post_save, sender=PurchaseType)
def log_purchasetype_activity(sender, instance, created, **kwargs):
    """Log PurchaseType CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        object_repr = instance.name
        description = f"Active: {instance.is_active}"

        log_activity(
            user, action, "PurchaseType", instance.id, object_repr, description
        )


@receiver(post_delete, sender=PurchaseType)
def log_purchasetype_delete(sender, instance, **kwargs):
    """Log PurchaseType DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        object_repr = instance.name
        log_activity(user, "DELETE", "PurchaseType", instance.id, object_repr)


# TaxTable Activity Logging
@receiver(post_save, sender=TaxTable)
def log_taxtable_activity(sender, instance, created, **kwargs):
    """Log TaxTable CREATE and UPDATE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        action = "CREATE" if created else "UPDATE"
        purchase_type = (
            str(instance.purchase_type) if instance.purchase_type else "Unknown"
        )
        object_repr = f"Tax Table: {purchase_type}"
        description = f"Purchase Type: {purchase_type}"

        log_activity(user, action, "TaxTable", instance.id, object_repr, description)

        create_notifications_for_active_users(
            title="Financial analysis notification",
            message=(
                f"Tax configuration for {purchase_type} was "
                f"{'added' if created else 'updated'} and is now available for analysis."
            ),
            level=Notification.LEVEL_INFO,
            category=Notification.CATEGORY_FINANCIAL_ANALYSIS,
            actor=user,
            event_key=(
                f"tax-table-create-{instance.id}"
                if created
                else f"tax-table-update-{instance.id}-{timezone.localdate().isoformat()}"
            ),
        )


@receiver(post_delete, sender=TaxTable)
def log_taxtable_delete(sender, instance, **kwargs):
    """Log TaxTable DELETE activities"""
    user = get_current_user()

    if user and user.is_authenticated:
        purchase_type = (
            str(instance.purchase_type) if instance.purchase_type else "Unknown"
        )
        object_repr = f"Tax Table: {purchase_type}"
        log_activity(user, "DELETE", "TaxTable", instance.id, object_repr)


@receiver(post_save, sender=Notification)
def push_notification_realtime(sender, instance, created, **kwargs):
    """Broadcast notification create/update events to the target user in realtime."""
    created_at_local = instance.get_created_at_local()
    read_at_local = instance.get_read_at_local()
    payload = {
        "id": instance.id,
        "title": instance.title,
        "message": instance.message,
        "level": instance.level,
        "category": instance.category,
        "is_read": instance.is_read,
        "created_at": created_at_local.isoformat() if created_at_local else None,
        "read_at": read_at_local.isoformat() if read_at_local else None,
        "created_display": instance.get_created_display(),
        "read_display": instance.get_read_display(),
    }
    broadcast_to_user(
        instance.user,
        "notification.new" if created else "notification.updated",
        payload,
    )
