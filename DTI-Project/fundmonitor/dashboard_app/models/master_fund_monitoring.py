"""Master Fund Monitoring Model - fund monitoring records"""

from django.db import models
from django.core.exceptions import ValidationError
from .supplier import Supplier
from .staff import Staff, Division
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_string_length,
    validate_date_not_in_future,
    validate_check_number_format,
    validate_mooe_format,
    sanitize_string_input,
    validate_no_script_content,
)


class MasterFundMonitoring(models.Model):
    """Master fund monitoring records"""
    
    # Transaction Information
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name='monitoring_records',
        help_text="Budget division",
        null=True,
        blank=True,
    )
    fund_source = models.ForeignKey(
        'FundSource',
        on_delete=models.CASCADE,
        related_name='monitoring_records',
        help_text="Fund source for transaction",
        null=True,
        blank=True,
    )
    mooe = models.CharField(
        max_length=100,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_mooe_format,
        ],
        help_text="MOOE category code",
        null=True,
        blank=True,
    )
    nc = models.ForeignKey(
        'NegosyoCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitoring_records',
        help_text="Negosyo Center"
    )
    date = models.DateField(
        validators=[validate_date_not_in_future],
        help_text="Transaction date"
    )
    payee = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='monitoring_records',
        help_text="Supplier/Payee"
    )
    particulars = models.TextField(
        validators=[validate_string_length(min_length=5, max_length=500)],
        help_text="Transaction details"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('Disbursement', 'Disbursement'),
            ('Downloads', 'Downloads'),
            ('Refund', 'Refund'),
            ('Adjustment', 'Adjustment'),
        ],
        default='Disbursement',
        help_text="Type of transaction"
    )
    
    # TIN and Tax Information
    tin = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Auto-populated from Supplier"
    )
    tax_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Auto-populated from Supplier VAT Status"
    )
    purchase_type = models.ForeignKey(
        'PurchaseType',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='monitoring_records',
        help_text="Type of purchase with associated tax rates"
    )
    
    # Financial Details
    payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
        help_text="Payment amount"
    )
    dv_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Disbursement Voucher number"
    )
    downloads = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
        help_text="Downloads"
    )
    cheque_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[validate_check_number_format],
        help_text="Check number"
    )
    cleared_date = models.DateField(
        blank=True,
        null=True,
        validators=[validate_date_not_in_future],
        help_text="Date transaction was cleared"
    )
    account_title = models.ForeignKey(
        'ExpenseObject',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='monitoring_accounts',
        help_text="Account/Expense object"
    )
    
    # Tax Breakdown (First Set)
    goods_5_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods 5% tax"
    )
    services_5_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Services 5% tax"
    )
    goods_services_3_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods/Services 3% tax"
    )
    goods_1_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods 1% tax"
    )
    services_2_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Services 2% tax"
    )
    rental_5_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Rental 5% tax"
    )
    prof_fee_10_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Professional fee 10% tax"
    )
    
    # Additional Information
    expense_classification = models.ForeignKey(
        'ExpenseCategory',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='monitoring_expenses',
        help_text="Expense classification"
    )
    cheque_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Cleared', 'Cleared'),
            ('Bounced', 'Bounced'),
        ],
        default='Pending',
        help_text="Cheque/Payment status"
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='monitoring_records',
        help_text="Responsible staff member"
    )
    
    # Tax Breakdown (Second Set)
    goods_5_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods 5% tax (2)"
    )
    services_5_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Services 5% tax (2)"
    )
    goods_services_1_percent = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods/Services 1% tax"
    )
    goods_1_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Goods 1% tax (2)"
    )
    services_2_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Services 2% tax (2)"
    )
    rental_5_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Rental 5% tax (2)"
    )
    prof_fee_10_percent_2 = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True, default=0,
        validators=[validate_transaction_amount],
        help_text="Professional fee 10% tax (2)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Master Fund Monitoring"
        verbose_name_plural = "Master Fund Monitorings"

    def __str__(self):
        return f"{self.payee.supplier} - {self.date}"
    
    def clean(self):
        """Validate master fund monitoring data"""
        self.particulars = sanitize_string_input(self.particulars)
        validate_no_script_content(self.particulars)
        
        # Validate cleared_date is after transaction date
        if self.cleared_date and self.cleared_date < self.date:
            raise ValidationError({
                'cleared_date': 'Cleared date must be on or after the transaction date.'
            })
        
        # Validate that at least a payment amount is recorded
        if self.payments == 0:
            # Optional validation - can be removed if payments should always be 0
            pass
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
