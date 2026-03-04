"""Bank Statement Forms - BankStatementForm"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from dashboard_app.models import BankStatement
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_date_not_in_future,
    sanitize_string_input,
    validate_no_script_content,
    validate_check_number_format,
)


class BankStatementForm(forms.ModelForm):
    """Form for creating and editing bank statement entries"""
    
    class Meta:
        model = BankStatement
        fields = ['date', 'description', 'check_number', 'debit', 'credit', 'balance', 'status']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control has-prefix',
                'type': 'date',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Transaction description',
                'required': True
            }),
            'check_number': forms.TextInput(attrs={
                'class': 'form-control has-prefix',
                'placeholder': 'Check/Reference number (optional)'
            }),
            'debit': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'credit': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
            }),
            'status': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
    
    def __init__(self, *args, is_first_transaction=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_first_transaction = is_first_transaction
        
        # Make balance readonly for subsequent transactions
        if not is_first_transaction:
            self.fields['balance'].widget.attrs['readonly'] = True
            self.fields['balance'].widget.attrs['class'] = 'form-control has-prefix-text'
    
    def clean_date(self):
        """Validate transaction date"""
        date = self.cleaned_data.get('date')
        
        if not date:
            raise ValidationError('Transaction date is required.', code='required')
        
        try:
            validate_date_not_in_future(date)
        except ValidationError:
            raise ValidationError('Transaction date cannot be in the future.', code='future_date')
        
        return date
    
    def clean_description(self):
        """Validate description"""
        description = self.cleaned_data.get('description', '').strip()
        
        if not description:
            raise ValidationError('Description is required. Please provide details about the transaction.', code='required')
        
        if len(description) > 255:
            raise ValidationError('Description must not exceed 255 characters. Please shorten the description.', code='max_length')
        
        try:
            validate_no_script_content(description)
        except ValidationError:
            raise ValidationError('Description contains invalid content. Please remove any special tags or scripts.', code='script_injection')
        
        return sanitize_string_input(description)
    
    def clean_check_number(self):
        """Validate check number"""
        check_number = self.cleaned_data.get('check_number', '').strip()
        
        if not check_number:
            return ''
        
        try:
            validate_check_number_format(check_number)
        except ValidationError:
            raise ValidationError(
                'Invalid check number format. Use only uppercase letters, numbers, and hyphens.',
                code='invalid_format'
            )
        
        return check_number
    
    def clean_debit(self):
        """Validate debit amount"""
        debit = self.cleaned_data.get('debit')
        
        if debit is None or debit == 0 or debit == '':
            return debit or 0
        
        try:
            validate_transaction_amount(debit)
        except ValidationError:
            raise ValidationError('Debit amount must be a valid positive number. Please check the amount entered.', code='invalid_amount')
        
        return debit
    
    def clean_credit(self):
        """Validate credit amount"""
        credit = self.cleaned_data.get('credit')
        
        if credit is None or credit == 0 or credit == '':
            return credit or 0
        
        try:
            validate_transaction_amount(credit)
        except ValidationError:
            raise ValidationError('Credit amount must be a valid positive number. Please check the amount entered.', code='invalid_amount')
        
        return credit
    
    def clean_balance(self):
        """Validate balance"""
        balance = self.cleaned_data.get('balance')
        
        # For first transaction, balance is required
        if self.is_first_transaction:
            if not balance and balance != 0:
                raise ValidationError('Balance is required for the first transaction. Please enter the opening balance.', code='required')
            
            # Validate the balance value
            try:
                validate_transaction_amount(balance)
            except ValidationError:
                raise ValidationError('Balance must be a valid positive number.', code='invalid_amount')
        
        # For subsequent transactions, balance can be any value (will be auto-calculated)
        return balance or 0
    
    def clean_status(self):
        """Validate status"""
        status = self.cleaned_data.get('status')
        
        if not status:
            raise ValidationError('Status is required. Please select a status.', code='required')
        
        valid_choices = [choice[0] for choice in BankStatement.CATEGORY_CHOICES]
        if status not in valid_choices:
            raise ValidationError('Invalid status selection. Please select a valid status.', code='invalid_choice')
        
        return status
    
    def clean(self):
        """Cross-field validations"""
        cleaned_data = super().clean()
        debit = cleaned_data.get('debit') or 0
        credit = cleaned_data.get('credit') or 0
        
        # Ensure not both debit and credit have values
        if debit > 0 and credit > 0:
            raise ValidationError(
                'Invalid transaction: Cannot have both debit and credit amounts in the same transaction. Please enter either a debit or credit, not both.',
                code='both_debit_credit'
            )
        
        # Validate that at least one is non-zero
        if debit == 0 and credit == 0:
            raise ValidationError(
                'At least one of debit or credit must be entered.',
                code='no_amount'
            )
        
        # For subsequent transactions, calculate balance automatically from previous transaction
        if not self.is_first_transaction:
            # Get the last transaction's balance
            last_transaction = BankStatement.objects.exclude(id=self.instance.id if self.instance.id else None).order_by('-date', '-created_at').first()
            
            if last_transaction:
                previous_balance = Decimal(str(last_transaction.balance))
                # Calculate: Previous Balance + Credit - Debit using Decimal for precision
                calculated_balance = previous_balance + Decimal(str(credit)) - Decimal(str(debit))
                cleaned_data['balance'] = calculated_balance
            else:
                # Shouldn't happen, but just in case
                cleaned_data['balance'] = Decimal(str(credit)) - Decimal(str(debit))
        
        return cleaned_data
