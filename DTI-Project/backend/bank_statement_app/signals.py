"""Signal handlers owned by bank_statement_app."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from bank_statement_app.models import BankStatement
from mater_fundmonitor_app.models import MasterFundMonitoring


@receiver(post_save, sender=BankStatement)
def sync_cheque_status_to_monitoring(sender, instance, created, **kwargs):
    """Sync monitoring cheque status and cleared date whenever a bank statement record is saved."""
    if not instance.check_number:
        return

    matching_records = MasterFundMonitoring.objects.filter(
        cheque_number=instance.check_number
    )
    status_mapping = {
        "Cleared": "Cleared",
        "On Process": "Pending",
    }
    new_status = status_mapping.get(instance.status, "Pending")

    # Build update dict with status and cleared_date if applicable
    update_dict = {"cheque_status": new_status}
    if instance.status == "Cleared":
        update_dict["cleared_date"] = instance.date
    else:
        # If marked as not cleared, clear the cleared_date
        update_dict["cleared_date"] = None

    matching_records.update(**update_dict)


@receiver(post_save, sender=MasterFundMonitoring)
def sync_cheque_status_from_bank_statement(
    sender, instance, created, update_fields, **kwargs
):
    """Sync monitoring status and cleared date from matching bank statement when cheque number changes."""
    if update_fields and (
        update_fields == {"cheque_status"}
        or update_fields == {"cheque_status", "cleared_date"}
    ):
        return

    if not instance.cheque_number:
        return

    bank_statement = BankStatement.objects.filter(
        check_number=instance.cheque_number
    ).first()
    if bank_statement:
        status_mapping = {
            "Cleared": "Cleared",
            "On Process": "Pending",
        }
        new_status = status_mapping.get(bank_statement.status, "Pending")
        cleared_date = (
            bank_statement.date if bank_statement.status == "Cleared" else None
        )

        # Only update if status or cleared_date has changed
        if (
            instance.cheque_status != new_status
            or instance.cleared_date != cleared_date
        ):
            instance.cheque_status = new_status
            instance.cleared_date = cleared_date
            instance.save(update_fields=["cheque_status", "cleared_date"])
    elif instance.cheque_status != "Pending":
        # If no matching bank statement, set to pending
        instance.cheque_status = "Pending"
        instance.cleared_date = None
        instance.save(update_fields=["cheque_status", "cleared_date"])
