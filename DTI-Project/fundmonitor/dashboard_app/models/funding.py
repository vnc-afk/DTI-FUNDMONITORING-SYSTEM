from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import date
from .supplier import Supplier
from .staff import Staff, Division
from dashboard_app.validators import (
    validate_budget_amount,
    validate_transaction_amount,
    validate_non_negative_number,
    validate_string_length,
    validate_letters_only,
    validate_hex_color,
    validate_date_not_in_future,
    validate_dv_number_format,
    validate_check_number_format,
    validate_mooe_format,
    validate_nc_format,
    validate_numeric_only,
    sanitize_string_input,
    validate_no_script_content,
)


class FundSource(models.Model):
    """Fund sources for budget allocation"""
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            validate_string_length(min_length=2, max_length=100),
        ],
        help_text="Fund source name"
    )
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[validate_budget_amount],
        help_text="Annual budget allocation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Fund Source"
        verbose_name_plural = "Fund Sources"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate fund source data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        # Check uniqueness on update
        if self.id:
            duplicate = FundSource.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A fund source with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BankAccount(models.Model):
    """Bank account with opening balance"""
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Bank account name"
    )
    account_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Bank account number"
    )
    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Opening balance for the account"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this account currently active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.name} ({self.account_number})"
    
    def clean(self):
        """Validate bank account data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Bank account name must be at least 2 characters.'})
        
        if not self.account_number or len(self.account_number.strip()) < 5:
            raise ValidationError({'account_number': 'Account number must be at least 5 characters.'})
        
        # Check uniqueness for name on update
        if self.id:
            duplicate_name = BankAccount.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate_name:
                raise ValidationError({'name': 'A bank account with this name already exists.'})
            
            duplicate_acc = BankAccount.objects.filter(
                account_number=self.account_number
            ).exclude(id=self.id).exists()
            if duplicate_acc:
                raise ValidationError({'account_number': 'This account number is already in use.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BankStatement(models.Model):
    """Bank statement entries with automatic balance calculation"""

    CATEGORY_CHOICES = [
        ('Cleared', 'Cleared'),
        ('On Process', 'On Process'),
    ]
    
    date = models.DateField(
        validators=[validate_date_not_in_future],
        help_text="Transaction date"
    )
    description = models.CharField(
        max_length=255,
        help_text="Transaction description"
    )
    check_number = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Check/Reference number (optional)"
    )
    debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
        help_text="Debit amount (money going out)"
    )
    credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
        help_text="Credit amount (money coming in)"
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Account balance"
    )
    status = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Transaction status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'created_at']
        verbose_name = "Bank Statement"
        verbose_name_plural = "Bank Statements"

    def __str__(self):
        return f"{self.date} - {self.description}"
    
    def _calculate_balance(self):
        """Calculate the balance for this transaction based on previous transactions"""
        # Normalize debit and credit values
        debit = self.debit or 0
        credit = self.credit or 0
        
        # Get all previous transactions ordered by date and creation time
        previous_statements = BankStatement.objects.exclude(id=self.id).order_by('date', 'created_at')
        
        # Filter to get transactions before this one
        previous_on_date = previous_statements.filter(date__lte=self.date)
        
        if not previous_on_date.exists():
            # This is the first transaction - balance is just the credit or debit
            return credit - debit
        else:
            # Get the last balance before this transaction
            last_statement = previous_on_date.last()
            previous_balance = last_statement.balance
            
            # Calculate new balance: Previous Balance + Credit - Debit
            new_balance = previous_balance + credit - debit
            return new_balance
    
    def clean(self):
        """Validate bank statement data"""
        self.description = sanitize_string_input(self.description)
        validate_no_script_content(self.description)
        
        # Validate debit/credit logic
        debit = self.debit or 0
        credit = self.credit or 0
        
        if debit > 0 and credit > 0:
            raise ValidationError(
                'Cannot have both debit and credit amounts in the same transaction.',
                code='both_debit_credit'
            )
        
        if debit == 0 and credit == 0:
            raise ValidationError(
                'At least one of debit or credit must be non-zero.',
                code='no_amount'
            )
    
    def save(self, *args, **kwargs):
        # Check if there are any previous transactions
        previous_statements = BankStatement.objects.exclude(id=self.id).order_by('-date', '-created_at')
        
        if previous_statements.exists():
            # Auto-calculate balance based on previous transactions
            # This overrides any user input for subsequent transactions
            self.balance = self._calculate_balance()
        elif self.balance is None:
            # First transaction - if balance is None, set to 0
            self.balance = 0
        
        self.full_clean()
        super().save(*args, **kwargs)


class MasterFundMonitoring(models.Model):
    """Master fund monitoring records"""
    
    # Transaction Information
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name='monitoring_records',
        help_text="Budget division"
    )
    fund_source = models.ForeignKey(
        FundSource,
        on_delete=models.CASCADE,
        related_name='monitoring_records',
        help_text="Fund source for transaction"
    )
    mooe = models.CharField(
        max_length=100,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_mooe_format,
        ],
        help_text="MOOE category code"
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
    purchase_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type of purchase"
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
    cheque_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[validate_check_number_format],
        help_text="Check number (optional)"
    )
    cleared_date = models.DateField(
        blank=True,
        null=True,
        validators=[validate_date_not_in_future],
        help_text="Date transaction was cleared (optional)"
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
        help_text="Expense classification (optional)"
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
        help_text="Responsible staff member (optional)"
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


class ExpenseObject(models.Model):
    """Expense objects with account codes"""
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            validate_string_length(min_length=5, max_length=50),
            validate_numeric_only,
        ],
        help_text="Numeric account code (e.g., '5020101000')"
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_string_length(min_length=3, max_length=255)],
        help_text="Description of expense object"
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        validators=[validate_hex_color],
        help_text="Hex color for display (#RRGGBB)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[validate_string_length(max_length=500)],
        help_text="Additional details (optional)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = "Expense Object"
        verbose_name_plural = "Expense Objects"

    def __str__(self):
        return f"({self.code}) {self.name}"
    
    def clean(self):
        """Validate expense object data"""
        self.name = sanitize_string_input(self.name)
        if self.description:
            self.description = sanitize_string_input(self.description)
        
        validate_no_script_content(self.name)
        if self.description:
            validate_no_script_content(self.description)
        
        # Check uniqueness for code on update
        if self.id:
            duplicate = ExpenseObject.objects.filter(
                code=self.code
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'code': 'This expense code is already in use.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    """Expense categories for classification"""
    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_string_length(min_length=2, max_length=255)],
        help_text="Category name"
    )
    color = models.CharField(
        max_length=7,
        default='#95a5a6',
        validators=[validate_hex_color],
        help_text="Hex color for display (#RRGGBB)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[validate_string_length(max_length=500)],
        help_text="Category description (optional)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate expense category data"""
        self.name = sanitize_string_input(self.name)
        if self.description:
            self.description = sanitize_string_input(self.description)
        
        validate_no_script_content(self.name)
        if self.description:
            validate_no_script_content(self.description)
        
        # Check uniqueness for name on update
        if self.id:
            duplicate = ExpenseCategory.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A category with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class FundSourceBreakdown(models.Model):
    """Breakdown of fund sources by predefined categories"""
    
    fund_source = models.ForeignKey(
        FundSource,
        on_delete=models.CASCADE,
        related_name='breakdowns',
        help_text="Associated fund source"
    )
    category = models.ForeignKey(
        'BreakdownCategory',
        on_delete=models.CASCADE,
        related_name='fund_breakdowns',
        blank=True,
        null=True,
        help_text="Breakdown category"
    )
    budget_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[validate_transaction_amount],
        help_text="Budget allocation for this category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fund_source', 'category__order', 'category__code']
        verbose_name = "Fund Source Breakdown"
        verbose_name_plural = "Fund Source Breakdowns"
        unique_together = ('fund_source', 'category')

    def __str__(self):
        return f"{self.fund_source.name} - {self.category.code}"
    
    def clean(self):
        """Validate breakdown data"""
        # Only validate if fund_source_id is set
        if not self.fund_source_id or not self.budget_amount:
            return
        
        # Validate budget amount doesn't exceed fund source annual budget
        total_breakdown = FundSourceBreakdown.objects.filter(
            fund_source_id=self.fund_source_id
        ).exclude(id=self.id).aggregate(total=Sum('budget_amount'))['total'] or 0
        
        if total_breakdown + self.budget_amount > self.fund_source.annual_budget:
            raise ValidationError({
                'budget_amount': f'Total breakdown ({total_breakdown + self.budget_amount}) cannot exceed annual budget ({self.fund_source.annual_budget}).'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BreakdownCategory(models.Model):
    """Budget breakdown categories"""
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Category code (e.g., OO1, 4.1A)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Category description"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this category active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'code']
        verbose_name = "Breakdown Category"
        verbose_name_plural = "Breakdown Categories"

    def __str__(self):
        return f"({self.code}) {self.name}"
    
    def clean(self):
        """Validate breakdown category data"""
        self.code = self.code.upper().strip()
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        if not self.code or len(self.code.strip()) < 1:
            raise ValidationError({'code': 'Code is required.'})
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = BreakdownCategory.objects.filter(
                code__iexact=self.code
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'code': 'A category with this code already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class District(models.Model):
    """Districts for Negosyo Center organization"""
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="District name (e.g., District 1, District 2)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the district"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this district active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "District"
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate district data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'District name must be at least 2 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = District.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A district with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class NegosyoCenter(models.Model):
    """Negosyo Centers organized by district"""
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='negosyo_centers',
        help_text="Parent district"
    )
    name = models.CharField(
        max_length=100,
        help_text="Negosyo Center name"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for the NC (e.g., sto_domingo)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the NC"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this NC active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district__order', 'district__name', 'name']
        verbose_name = "Negosyo Center"
        verbose_name_plural = "Negosyo Centers"
        unique_together = ('district', 'code')

    def __str__(self):
        return f"{self.name} ({self.district.name})"
    
    def clean(self):
        """Validate negosyo center data"""
        self.name = sanitize_string_input(self.name)
        self.code = self.code.lower().strip()
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'NC name must be at least 2 characters.'})
        
        if not self.code or len(self.code.strip()) < 2:
            raise ValidationError({'code': 'NC code must be at least 2 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = NegosyoCenter.objects.filter(
                code__iexact=self.code
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'code': 'A NC with this code already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
