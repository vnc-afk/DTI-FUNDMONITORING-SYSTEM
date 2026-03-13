"""Bank Models - bank accounts and statement management"""

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_date_not_in_future,
    sanitize_string_input,
    validate_no_script_content,
)


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
        help_text="Check/Reference number"
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
        default='On Process',
        null=True,
        blank=True,
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
        
        # Validate balance is not negative
        if self.balance is not None and self.balance < 0:
            raise ValidationError(
                'Balance cannot be negative. Please check the transaction amounts or opening balance.',
                code='negative_balance'
            )
    
    def save(self, *args, **kwargs):
        # Check if this is the first chronological transaction
        first_transaction = BankStatement.objects.exclude(id=self.id).order_by('date', 'created_at').first()
        
        is_first_transaction = not first_transaction
        
        if not is_first_transaction and self.created_at:
            # Compare dates and creation times only if created_at exists
            is_first_transaction = (
                first_transaction.date > self.date or 
                (first_transaction.date == self.date and first_transaction.created_at > self.created_at)
            )
        
        if is_first_transaction:
            # For first transaction, preserve user's balance input or default to 0
            if self.balance is None:
                self.balance = 0
        else:
            # For subsequent transactions, auto-calculate balance based on previous transactions
            self.balance = self._calculate_balance()
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # If this is the first transaction, recalculate all subsequent transactions
        if is_first_transaction:
            subsequent_transactions = BankStatement.objects.exclude(id=self.id).order_by('date', 'created_at')
            for transaction in subsequent_transactions:
                # Recalculate balance for each subsequent transaction
                transaction.balance = transaction._calculate_balance()
                # Save without triggering this same logic again
                super(BankStatement, transaction).save(update_fields=['balance', 'updated_at'])
