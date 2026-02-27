from django.db import models
from .supplier import Supplier


class FundSource(models.Model):
    name = models.CharField(max_length=100)
    annual_budget = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.name


class BudgetBreakdown(models.Model):
    fund_source = models.ForeignKey(FundSource, on_delete=models.CASCADE, related_name='breakdowns')
    category = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.fund_source.name} - {self.category}"


class BankStatement(models.Model):

    CATEGORY_CHOICES = [
        ('Cleared', 'Cleared'),
        ('On Process', 'On Process'),
    ]
    
    date = models.DateField()
    description = models.CharField(max_length=255)
    check_number = models.CharField(max_length=50, blank=True, default='')
    debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.description


class MasterFundMonitoring(models.Model):
    CHEQUE_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Cleared', 'Cleared'),
        ('Bounced', 'Bounced'),
    ]
    
    # Transaction Information
    division = models.CharField(max_length=100)
    fund_source = models.ForeignKey(FundSource, on_delete=models.CASCADE, related_name='monitoring_records')
    mooe = models.CharField(max_length=100)  # MOOE Category
    nc = models.CharField(max_length=100)   # NC Category
    date = models.DateField()
    payee = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='monitoring_records')
    particulars = models.TextField()
    
    # TIN and Tax Information
    tin = models.CharField(max_length=20, blank=True, null=True)  # Auto-populated from Supplier
    tax_type = models.CharField(max_length=100, blank=True, null=True)  # Auto-populated from Supplier VAT Status
    purchase_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial Details
    downloads = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    payments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    dv_number = models.CharField(max_length=50, blank=True, null=True)
    cheque_number = models.CharField(max_length=50, blank=True, null=True)
    cleared_date = models.DateField(blank=True, null=True)
    account_title = models.CharField(max_length=255, blank=True, null=True)
    
    # Tax Breakdown (First Set)
    goods_5_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    services_5_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    goods_services_3_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    goods_1_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    services_2_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    rental_5_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    prof_fee_10_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    
    # Additional Information
    expense_classification = models.CharField(max_length=100, blank=True, null=True)
    cheque_status = models.CharField(max_length=20, choices=CHEQUE_STATUS_CHOICES, default='Pending')
    staff = models.CharField(max_length=255, blank=True, null=True)
    
    # Tax Breakdown (Second Set)
    goods_5_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    services_5_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    goods_services_1_percent = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    goods_1_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    services_2_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    rental_5_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    prof_fee_10_percent_2 = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payee.supplier} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Master Fund Monitoring"
        verbose_name_plural = "Master Fund Monitorings"
