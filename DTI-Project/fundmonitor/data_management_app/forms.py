from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from data_management_app.models import (
    Staff,
    Supplier,
    FundSource,
    FundSourceBreakdown,
    TaxTable,
    PurchaseType,
    ExpenseObject,
    ExpenseCategory,
)
from dashboard_app.utils.validators import (
    validate_letters_only,
    sanitize_string_input,
    validate_no_script_content,
    validate_tin_format,
    validate_phone_number,
    validate_alphanumeric_with_spaces,
    validate_transaction_amount,
)


class ImportDataForm(forms.Form):
    """Form for importing data from Excel/CSV files."""

    DATA_TYPE_CHOICES = [
        ('supplier', 'Suppliers'),
        ('bank_statement', 'Bank Statements'),
        ('master_fund_monitoring', 'Master Fund Monitoring'),
        ('staff', 'Staff'),
    ]

    data_type = forms.ChoiceField(
        choices=DATA_TYPE_CHOICES,
        label='What data are you importing?',
        widget=forms.RadioSelect,
    )

    file = forms.FileField(
        label='Select Excel or CSV file',
        help_text='Supported formats: .xlsx, .xls, .csv',
        widget=forms.FileInput(attrs={
            'accept': '.xlsx,.xls,.csv',
            'class': 'form-control',
        })
    )

    sheet_name = forms.CharField(
        label='Sheet name (for Excel files)',
        help_text='Leave blank to use first sheet. Or specify sheet name.',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Suppliers, Bank Statements, Sheet1',
        })
    )

    skip_rows = forms.IntegerField(
        label='Skip rows',
        help_text='Number of rows to skip before the header (e.g., if your file has a title row, set this to 1)',
        required=False,
        initial=0,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0',
        })
    )

    skip_errors = forms.BooleanField(
        required=False,
        label='Skip errors and continue importing',
        help_text='If checked, rows with errors will be skipped. If unchecked, import will stop at first error.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    'File format not supported. Please upload .xlsx, .xls, or .csv file'
                )

            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10MB')

        return file


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name (letters only)', 'required': True}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., J', 'maxlength': '5'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name (letters only)', 'required': True}),
            'division': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError('First name is required.', code='required')
        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.', code='min_length')
        if len(first_name) > 100:
            raise ValidationError('First name must not exceed 100 characters.', code='max_length')
        try:
            validate_letters_only(first_name)
        except ValidationError:
            raise ValidationError('First name must contain only letters, spaces, hyphens, periods, and apostrophes.', code='invalid_chars')
        try:
            validate_no_script_content(first_name)
        except ValidationError:
            raise ValidationError('First name contains invalid content.', code='script_injection')
        return sanitize_string_input(first_name)

    def clean_middle_initial(self):
        middle_initial = self.cleaned_data.get('middle_initial', '').strip()
        if not middle_initial:
            return ''
        if len(middle_initial) > 5:
            raise ValidationError('Middle initial must not exceed 5 characters.', code='max_length')
        try:
            validate_letters_only(middle_initial)
        except ValidationError:
            raise ValidationError('Middle initial must contain only letters.', code='invalid_chars')
        try:
            validate_no_script_content(middle_initial)
        except ValidationError:
            raise ValidationError('Middle initial contains invalid content.', code='script_injection')
        return sanitize_string_input(middle_initial)

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError('Last name is required.', code='required')
        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.', code='min_length')
        if len(last_name) > 100:
            raise ValidationError('Last name must not exceed 100 characters.', code='max_length')
        try:
            validate_letters_only(last_name)
        except ValidationError:
            raise ValidationError('Last name must contain only letters, spaces, hyphens, periods, and apostrophes.', code='invalid_chars')
        try:
            validate_no_script_content(last_name)
        except ValidationError:
            raise ValidationError('Last name contains invalid content.', code='script_injection')
        return sanitize_string_input(last_name)

    def clean_division(self):
        division = self.cleaned_data.get('division')
        if not division:
            raise ValidationError('Division is required.', code='required')
        return division

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        if first_name and last_name and first_name.lower() == last_name.lower():
            raise ValidationError('First name and last name must be different.', code='same_names')
        return cleaned_data


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name', 'required': True}),
            'tin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '###-###-###-###', 'maxlength': '50'}),
            'vat_status': forms.Select(attrs={'class': 'form-select'}),
            'philgeps_registration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PhilGEPS code (optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Complete business address'}),
            'propprietor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proprietor/Owner name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Philippine phone number', 'maxlength': '20'}),
        }

    def clean_supplier(self):
        supplier = self.cleaned_data.get('supplier', '').strip()
        if not supplier:
            raise ValidationError('Supplier name is required.', code='required')
        if len(supplier) < 2:
            raise ValidationError('Supplier name must be at least 2 characters long.', code='min_length')
        if len(supplier) > 200:
            raise ValidationError('Supplier name must not exceed 200 characters.', code='max_length')
        try:
            validate_alphanumeric_with_spaces(supplier)
        except ValidationError:
            raise ValidationError('Supplier name must contain only letters, numbers, spaces, hyphens, and periods.', code='invalid_chars')
        try:
            validate_no_script_content(supplier)
        except ValidationError:
            raise ValidationError('Supplier name contains invalid content.', code='script_injection')

        queryset = Supplier.objects.filter(supplier__iexact=supplier)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError('A supplier with this name already exists.', code='unique')
        return sanitize_string_input(supplier)

    def clean_tin(self):
        tin = self.cleaned_data.get('tin')
        if not tin:
            return ''
        tin = str(tin).strip()
        if not tin:
            return ''
        try:
            validate_tin_format(tin)
        except ValidationError:
            raise ValidationError('TIN must be in format: ###-###-###-### (12 digits with hyphens)', code='invalid_format')

        queryset = Supplier.objects.filter(tin=tin)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError('This TIN is already registered.', code='unique')
        return tin

    def clean_vat_status(self):
        vat_status = self.cleaned_data.get('vat_status')
        if not vat_status:
            return ''
        valid_choices = [choice[0] for choice in Supplier.CATEGORY_CHOICES]
        if vat_status not in valid_choices:
            raise ValidationError('Invalid VAT status selection.', code='invalid_choice')
        return vat_status

    def clean_philgeps_registration(self):
        philgeps = self.cleaned_data.get('philgeps_registration', '').strip()
        if not philgeps:
            return ''
        if len(philgeps) > 100:
            raise ValidationError('PhilGEPS registration must not exceed 100 characters.', code='max_length')
        try:
            validate_alphanumeric_with_spaces(philgeps)
        except ValidationError:
            raise ValidationError('PhilGEPS registration must contain only letters, numbers, spaces, hyphens, and periods.', code='invalid_chars')
        return sanitize_string_input(philgeps)

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            return ''
        address = str(address).strip()
        if not address:
            return ''
        if len(address) < 5:
            raise ValidationError('Address must be at least 5 characters long.', code='min_length')
        if len(address) > 500:
            raise ValidationError('Address must not exceed 500 characters.', code='max_length')
        try:
            validate_no_script_content(address)
        except ValidationError:
            raise ValidationError('Address contains invalid content.', code='script_injection')
        return sanitize_string_input(address)

    def clean_propprietor(self):
        proprietor = self.cleaned_data.get('propprietor')
        if not proprietor:
            return ''
        proprietor = str(proprietor).strip()
        if not proprietor:
            return ''
        if len(proprietor) < 2:
            raise ValidationError('Proprietor name must be at least 2 characters long.', code='min_length')
        if len(proprietor) > 200:
            raise ValidationError('Proprietor name must not exceed 200 characters.', code='max_length')
        try:
            validate_alphanumeric_with_spaces(proprietor)
        except ValidationError:
            raise ValidationError('Proprietor name must contain only letters, numbers, spaces, hyphens, and periods.', code='invalid_chars')
        try:
            validate_no_script_content(proprietor)
        except ValidationError:
            raise ValidationError('Proprietor name contains invalid content.', code='script_injection')
        return sanitize_string_input(proprietor)

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact:
            return ''
        contact = str(contact).strip()
        if not contact:
            return ''
        try:
            validate_phone_number(contact)
        except ValidationError:
            raise ValidationError('Please enter a valid Philippine phone number.', code='invalid_format')
        return contact


class FundSourceForm(forms.ModelForm):
    class Meta:
        model = FundSource
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fund source name', 'required': True}),
            'annual_budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'required': True, 'step': '0.01', 'min': '0'}),
        }


class FundSourceBreakdownForm(forms.ModelForm):
    class Meta:
        model = FundSourceBreakdown
        fields = ['category', 'budget_amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'budget_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'required': True, 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, fund_source=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fund_source = fund_source

    def clean_budget_amount(self):
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
        cleaned_data = super().clean()
        budget_amount = cleaned_data.get('budget_amount')
        category = cleaned_data.get('category')

        if not self.fund_source or budget_amount is None or not category:
            return cleaned_data

        query = FundSourceBreakdown.objects.filter(fund_source=self.fund_source, category=category)
        if self.instance and self.instance.pk:
            query = query.exclude(id=self.instance.pk)
        if query.exists():
            existing = query.first()
            raise ValidationError(
                f'Category {category.code} is already allocated ₱{existing.budget_amount:,.2f}. Please edit the existing breakdown or select a different category.',
                code='duplicate_breakdown'
            )

        exclude_kwargs = {}
        if self.instance and self.instance.pk:
            exclude_kwargs['id'] = self.instance.pk

        total_breakdown = FundSourceBreakdown.objects.filter(fund_source=self.fund_source).exclude(**exclude_kwargs).aggregate(total=Sum('budget_amount'))['total'] or 0
        if total_breakdown + budget_amount > self.fund_source.annual_budget:
            raise ValidationError(
                f'Total breakdown (₱{total_breakdown + budget_amount:,.2f}) cannot exceed annual budget (₱{self.fund_source.annual_budget:,.2f}).',
                code='exceeds_budget'
            )

        return cleaned_data


class TaxTableForm(forms.ModelForm):
    purchase_type = forms.ModelChoiceField(
        queryset=PurchaseType.objects.filter(is_active=True),
        empty_label='-- Select Purchase Type --',
        widget=forms.Select(attrs={'class': 'form-select', 'required': True, 'id': 'id_purchase_type'}),
        help_text='Select a purchase type'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        used_purchase_types = TaxTable.objects.values_list('purchase_type_id', flat=True)
        self.fields['purchase_type'].queryset = PurchaseType.objects.filter(is_active=True).exclude(id__in=used_purchase_types)
        if self.instance.pk:
            self.fields['purchase_type'].queryset = PurchaseType.objects.filter(is_active=True).exclude(id__in=used_purchase_types) | PurchaseType.objects.filter(id=self.instance.purchase_type_id)

    class Meta:
        model = TaxTable
        fields = ['purchase_type', 'vat_goods_5', 'vat_services_5', 'vat_goods_services_3', 'vat_goods_1', 'vat_services_2', 'vat_rental_5', 'vat_prof_fee_10']
        widgets = {
            'vat_goods_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_services_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_goods_services_3': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_goods_1': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_services_2': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_rental_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_prof_fee_10': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_purchase_type(self):
        purchase_type = self.cleaned_data.get('purchase_type')
        if not purchase_type:
            raise ValidationError('Purchase type is required.', code='required')

        queryset = TaxTable.objects.filter(purchase_type=purchase_type)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError('A tax entry for this purchase type already exists.', code='unique')
        return purchase_type


class ExpenseObjectForm(forms.ModelForm):
    class Meta:
        model = ExpenseObject
        fields = ['code', 'name', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5020101000', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense object name', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Expense category name', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


__all__ = [
    'ImportDataForm',
    'StaffForm',
    'SupplierForm',
    'FundSourceForm',
    'FundSourceBreakdownForm',
    'TaxTableForm',
    'ExpenseObjectForm',
    'ExpenseCategoryForm',
]
