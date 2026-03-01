from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal
from dashboard_app.models import FundSource, BankStatement, MasterFundMonitoring, Supplier, ExpenseObject, ExpenseCategory, Staff, Division, FundSourceBreakdown, NegosyoCenter, BreakdownCategory
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_budget_amount,
    validate_date_not_in_future,
    sanitize_string_input,
    validate_no_script_content,
    validate_dv_number_format,
    validate_check_number_format,
)


class FundSourceForm(forms.ModelForm):
    class Meta:
        model = FundSource
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fund source name',
                'required': True
            }),
            'annual_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'required': True,
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def clean_name(self):
        """Validate fund source name"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError('Fund source name is required. Please provide a name.', code='required')
        
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters. Please enter a longer name.', code='min_length')
        
        if len(name) > 100:
            raise ValidationError('Name cannot exceed 100 characters. Please shorten the name.', code='max_length')
        
        try:
            validate_no_script_content(name)
        except ValidationError:
            raise ValidationError('Name contains invalid content. Please remove any special tags or scripts.', code='script_injection')
        
        # Check uniqueness
        queryset = FundSource.objects.filter(name__iexact=name)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('A fund source with this name already exists. Please use a different name.', code='unique')
        
        return sanitize_string_input(name)
    
    def clean_annual_budget(self):
        """Validate annual budget"""
        budget = self.cleaned_data.get('annual_budget')
        
        if budget is None:
            raise ValidationError('Annual budget is required. Please enter a valid amount.', code='required')
        
        try:
            validate_budget_amount(budget)
        except ValidationError as e:
            raise e
        
        return budget


class BankStatementForm(forms.ModelForm):
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


class MasterFundMonitoringForm(forms.ModelForm):
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
    
    # Make fund_source a dropdown of fund sources
    fund_source = forms.ModelChoiceField(
        queryset=FundSource.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Fund Source'
    )
    
    # Make mooe a dropdown of breakdown categories
    mooe = forms.ModelChoiceField(
        queryset=BreakdownCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='MOOE',
        help_text='Maintenance and Other Operating Expenses'
    )
    
    # Make division a dropdown of divisions
    division = forms.ModelChoiceField(
        queryset=Division.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Division'
    )
    
    # Make nc a dropdown of Negosyo Centers
    nc = forms.ModelChoiceField(
        queryset=NegosyoCenter.objects.filter(is_active=True).select_related('district'),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True}),
        label='NC',
        required=True
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
            'purchase_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type of purchase'
            }),
            'payments': forms.NumberInput(attrs={
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
            
            # Tax Breakdown (First Set)
            'goods_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'services_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'goods_services_3_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'goods_1_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'services_2_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'rental_5_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'prof_fee_10_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            
            # Tax Breakdown (Second Set)
            'goods_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'services_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'goods_services_1_percent': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'goods_1_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'services_2_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'rental_5_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
            'prof_fee_10_percent_2': forms.NumberInput(attrs={
                'class': 'form-control has-prefix-text',
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def clean_mooe(self):
        """Validate and convert MOOE from BreakdownCategory to code"""
        mooe = self.cleaned_data.get('mooe')
        
        if not mooe:
            raise ValidationError('MOOE is required.', code='required')
        
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
        particulars = self.cleaned_data.get('particulars', '').strip()
        
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
        """Validate payments amount"""
        payments = self.cleaned_data.get('payments')
        
        if payments is None or payments == 0 or payments == '':
            return payments
        
        try:
            validate_transaction_amount(payments)
        except ValidationError:
            raise ValidationError('Payments amount must be a positive number.', code='invalid_amount')
        
        return payments
    
    def clean_dv_number(self):
        """Validate DV number"""
        dv_number = self.cleaned_data.get('dv_number', '').strip()
        
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
    
    def clean_cheque_number(self):
        """Validate cheque number"""
        cheque_number = self.cleaned_data.get('cheque_number', '').strip()
        
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


class FundSourceBreakdownForm(forms.ModelForm):
    """Form for fund source breakdown"""
    
    class Meta:
        model = FundSourceBreakdown
        fields = ['category', 'budget_amount']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'budget_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'required': True,
                'step': '0.01',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, fund_source=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fund_source = fund_source
    
    def clean_budget_amount(self):
        """Validate budget amount"""
        budget_amount = self.cleaned_data.get('budget_amount')
        
        if budget_amount is None:
            raise ValidationError('Budget amount is required.', code='required')
        
        if budget_amount <= 0:
            raise ValidationError('Budget amount must be greater than zero.', code='invalid')
        
        try:
            validate_transaction_amount(budget_amount)
        except ValidationError:
            raise ValidationError('Budget amount must be a valid positive number.', code='invalid_amount')
        
        return budget_amount
    
    def clean(self):
        """Validate total breakdown doesn't exceed annual budget"""
        cleaned_data = super().clean()
        budget_amount = cleaned_data.get('budget_amount')
        
        if not self.fund_source or budget_amount is None:
            return cleaned_data
        
        # Calculate total breakdown
        from django.db.models import Sum
        
        # Build exclude kwargs safely
        exclude_kwargs = {}
        if self.instance and self.instance.pk:
            exclude_kwargs['id'] = self.instance.pk
        
        total_breakdown = FundSourceBreakdown.objects.filter(
            fund_source=self.fund_source
        ).exclude(**exclude_kwargs).aggregate(
            total=Sum('budget_amount')
        )['total'] or 0
        
        if total_breakdown + budget_amount > self.fund_source.annual_budget:
            raise ValidationError(
                f'Total breakdown (₱{total_breakdown + budget_amount:,.2f}) cannot exceed annual budget (₱{self.fund_source.annual_budget:,.2f}).',
                code='exceeds_budget'
            )
        
        return cleaned_data
