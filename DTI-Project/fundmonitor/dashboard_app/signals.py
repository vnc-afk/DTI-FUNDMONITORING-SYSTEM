"""
Django signals for dashboard_app
Handles automatic sync between BankStatement and MasterFundMonitoring
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BankStatement, MasterFundMonitoring


@receiver(post_save, sender=BankStatement)
def sync_cheque_status_to_monitoring(sender, instance, created, **kwargs):
    """
    Auto-update MasterFundMonitoring cheque_status when BankStatement is updated.
    Matches by cheque_number and updates the status.
    """
    if not instance.check_number:
        # No cheque number to match
        return
    
    # Find all MasterFundMonitoring records with matching cheque_number
    # Note: BankStatement.check_number maps to MasterFundMonitoring.cheque_number
    matching_records = MasterFundMonitoring.objects.filter(
        cheque_number=instance.check_number
    )
    
    # Update their status based on the BankStatement status
    # Map BankStatement status to MasterFundMonitoring status
    status_mapping = {
        'Cleared': 'Cleared',
        'On Process': 'Pending',
    }
    
    new_status = status_mapping.get(instance.status, 'Pending')
    
    # Update all matching records with the new status
    updated_count = matching_records.update(cheque_status=new_status)
    
    if updated_count > 0:
        print(f"Auto-updated {updated_count} monitoring record(s) to status: {new_status}")


@receiver(post_save, sender=MasterFundMonitoring)
def sync_cheque_status_from_bank_statement(sender, instance, created, update_fields, **kwargs):
    """
    Auto-update MasterFundMonitoring cheque_status when cheque_number is set/updated.
    Checks BankStatement table to find actual status for that cheque number.
    """
    # Prevent infinite recursion - don't trigger if we're only updating cheque_status
    if update_fields and update_fields == {'cheque_status'}:
        return
    
    if not instance.cheque_number:
        # No cheque number to match
        return
    
    # Find matching BankStatement record with this cheque number
    bank_statement = BankStatement.objects.filter(
        check_number=instance.cheque_number
    ).first()
    
    if bank_statement:
        # Found a matching bank statement - update the status to match
        status_mapping = {
            'Cleared': 'Cleared',
            'On Process': 'Pending',
        }
        new_status = status_mapping.get(bank_statement.status, 'Pending')
        
        # Update the cheque_status only if it's different
        if instance.cheque_status != new_status:
            instance.cheque_status = new_status
            instance.save(update_fields=['cheque_status'])
    else:
        # No matching bank statement - set to Pending
        if instance.cheque_status != 'Pending':
            instance.cheque_status = 'Pending'
            instance.save(update_fields=['cheque_status'])
