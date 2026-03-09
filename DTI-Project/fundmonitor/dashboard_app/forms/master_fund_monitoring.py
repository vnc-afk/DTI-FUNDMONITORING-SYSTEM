"""Master Fund Monitoring Forms - MasterFundMonitoringForm"""

from django import forms
from django.core.exceptions import ValidationError
from dashboard_app.models import (
    MasterFundMonitoring, Supplier, FundSource, BreakdownCategory,
    Division, NegosyoCenter, ExpenseObject, ExpenseCategory, Staff, PurchaseType
)
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_date_not_in_future,
    sanitize_string_input,
    validate_no_script_content,
    validate_dv_number_format,
    validate_check_number_format,
)


class MasterFundMonitoringForm(forms.ModelForm):
    """Form for creating and editing master fund monitoring records"""
    
    # Make payee a dropdown of suppliers
    payee = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'payeeSelect',
            'required': True
        }),
        label='Payee'
    )
    
    # Make fund_source a dropdown of fund sources (required)
    fund_source = forms.ModelChoiceField(
        queryset=FundSource.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Fund Source',
        required=True,
        error_messages={
            'required': 'Please select a Fund Source.'
        }
    )
    
    # Make mooe a dropdown of breakdown categories (optional)
    mooe = forms.ModelChoiceField(
        queryset=BreakdownCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='MOOE',
        help_text='Maintenance and Other Operating Expenses',
        required=False
    )
    
    # Make division a dropdown of divisions (optional)
    division = forms.ModelChoiceField(
        queryset=Division.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Division',
        required=False
    )
    
    # Make nc a dropdown of Negosyo Centers (optional)
    nc = forms.ModelChoiceField(
        queryset=NegosyoCenter.objects.filter(is_active=True).select_related('district'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='NC',
        required=False
    )
    
    # Make account_title a dropdown of expense objects
    account_title = forms.ModelChoiceField(
        queryset=ExpenseObject.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Account Title',
        required=False
    )
    
    # Make expense_classification a dropdown of expense categories
    expense_classification = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Expense Classification',
        required=False
    )
    
    # Make staff a dropdown of staff members
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Staff',
        required=False
    )
    
    # Make purchase_type a dropdown of purchase types
    purchase_type = forms.ModelChoiceField(
        queryset=PurchaseType.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'purchaseTypeSelect'
        }),
        label='Purchase Type',
        required=False
    )
    
    # Transaction Type - Disbursement, Refund, or Adjustment
    transaction_type = forms.ChoiceField(
        choices=[
            ('Disbursement', 'Disbursement'),
            ('Refund', 'Refund'),
            ('Adjustment', 'Adjustment'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'transaction-type-radio',
            'id': 'transactionTypeRadio'
        }),
        label='Transaction Type',
        initial='Disbursement',
        help_text='Select whether this is a disbursement, refund, or adjustment'
    )
    
    class Meta:
        model = MasterFundMonitoring
        exclude = ['cheque_status']  # cheque_status is auto-synced from BankStatement, not user-editable
        widgets = {
            # Transaction Information
            'date': forms.DateInput(attrs={
                'class': 'form-control has-prefix',
                'type': 'date',
                'required': True
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Transaction details',
                'required': True
            }),
            'transaction_type': forms.RadioSelect(attrs={
                'class': 'transaction-type-radio'
            }),
            
            # TIN and Tax Information
            'tin': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'tinField',
                'readonly': True
            }),
            'tax_type': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'taxTypeField',
                'readonly': True
            }),
            'payments': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'dv_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'DV number (optional)',
                'maxlength': '50'
            }),
            'downloads': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'cheque_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Check number (optional)',
                'maxlength': '50'
            }),
            'cleared_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            
            # Tax Breakdown (First Set) - Auto-calculated from tax table
            'goods_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'services_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'goods_services_3_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'goods_1_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'services_2_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'rental_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'prof_fee_10_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            
            # Tax Breakdown (Second Set) - Auto-calculated from tax table
            'goods_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'services_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'goods_services_1_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'goods_1_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'services_2_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'rental_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
            'prof_fee_10_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0',
                'readonly': True
            }),
        }
    
    def clean_mooe(self):
        """Validate and convert MOOE from BreakdownCategory to code"""
        mooe = self.cleaned_data.get('mooe')
        
        if not mooe:
            # leave blank/NULL value (model allows null)
            return None
        
        # If mooe is a BreakdownCategory object, extract its code
        if hasattr(mooe, 'code'):
            return mooe.code
        
        return mooe
    
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
    
    def clean_particulars(self):
        """Validate particulars"""
        particulars = (self.cleaned_data.get('particulars') or '').strip()
        
        if not particulars:
            raise ValidationError('Particulars is required.', code='required')
        
        if len(particulars) < 5:
            raise ValidationError('Particulars must be at least 5 characters long.', code='min_length')
        
        if len(particulars) > 500:
            raise ValidationError('Particulars must not exceed 500 characters.', code='max_length')
        
        try:
            validate_no_script_content(particulars)
        except ValidationError:
            raise ValidationError('Particulars contains invalid content.', code='script_injection')
        
        return sanitize_string_input(particulars)
    
    def clean_payments(self):
        """Validate payments amount; field is now required and must be positive."""
        payments = self.cleaned_data.get('payments')
        
        # Required check
        if payments in (None, ''):
            raise ValidationError('Payments amount is required.', code='required')
        
        try:
            validate_transaction_amount(payments)
        except ValidationError:
            raise ValidationError('Payments amount must be a positive number.', code='invalid_amount')
        
        return payments
    
    def clean_dv_number(self):
        """Validate DV number"""
        dv_number = (self.cleaned_data.get('dv_number') or '').strip()
        
        if not dv_number:
            return ''
        
        try:
            validate_dv_number_format(dv_number)
        except ValidationError:
            raise ValidationError(
                'DV number must contain only letters, numbers, and hyphens.',
                code='invalid_format'
            )
        
        return dv_number
    
    def clean_downloads(self):
        """Validate downloads amount"""
        downloads = self.cleaned_data.get('downloads')
        
        if downloads in (None, ''):
            return 0
        
        try:
            validate_transaction_amount(downloads)
        except ValidationError:
            raise ValidationError('Downloads amount must be a positive number.', code='invalid_amount')
        
        return downloads
    
    def clean_cheque_number(self):
        """Validate cheque number"""
        cheque_number = self.cleaned_data.get('cheque_number')
        # normalize None to empty string
        if not cheque_number:
            return ''
        cheque_number = str(cheque_number).strip()
        
        if not cheque_number:
            return ''
        
        try:
            validate_check_number_format(cheque_number)
        except ValidationError:
            raise ValidationError(
                'Cheque number must contain only letters, numbers, and hyphens.',
                code='invalid_format'
            )
        
        return cheque_number
    
    def clean_cleared_date(self):
        """Validate cleared date"""
        cleared_date = self.cleaned_data.get('cleared_date')
        
        if not cleared_date:
            return cleared_date
        
        try:
            validate_date_not_in_future(cleared_date)
        except ValidationError:
            raise ValidationError('Cleared date cannot be in the future.', code='future_date')
        
        return cleared_date
    
    def clean(self):
        """Cross-field validations"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        cleared_date = cleaned_data.get('cleared_date')
        
        # Validate cleared_date is after transaction date
        if date and cleared_date and cleared_date < date:
            raise ValidationError({
                'cleared_date': 'Cleared date must be on or after the transaction date.'
            })
        
        return cleaned_data
