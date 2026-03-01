from django import forms
from django.core.exceptions import ValidationError
from dashboard_app.models import Supplier
from dashboard_app.validators import (
    validate_tin_format,
    validate_phone_number,
    validate_alphanumeric_with_spaces,
    sanitize_string_input,
    validate_no_script_content,
)


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier name',
                'required': True
            }),
            'tin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '###-###-###-###',
                'required': True,
                'maxlength': '50'
            }),
            'vat_status': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'philgeps_registration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PhilGEPS code (optional)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete business address',
                'required': True
            }),
            'propprietor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Proprietor/Owner name',
                'required': True
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Philippine phone number',
                'required': True,
                'maxlength': '20'
            }),
        }
    
    def clean_supplier(self):
        """Validate supplier name"""
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
            raise ValidationError(
                'Supplier name must contain only letters, numbers, spaces, hyphens, and periods.',
                code='invalid_chars'
            )
        
        try:
            validate_no_script_content(supplier)
        except ValidationError:
            raise ValidationError('Supplier name contains invalid content.', code='script_injection')
        
        # Check uniqueness
        queryset = Supplier.objects.filter(supplier__iexact=supplier)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('A supplier with this name already exists.', code='unique')
        
        return sanitize_string_input(supplier)
    
    def clean_tin(self):
        """Validate TIN format"""
        tin = self.cleaned_data.get('tin', '').strip()
        
        if not tin:
            raise ValidationError('TIN is required.', code='required')
        
        try:
            validate_tin_format(tin)
        except ValidationError:
            raise ValidationError(
                'TIN must be in format: ###-###-###-### (12 digits with hyphens)',
                code='invalid_format'
            )
        
        # Check uniqueness
        queryset = Supplier.objects.filter(tin=tin)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('This TIN is already registered.', code='unique')
        
        return tin
    
    def clean_vat_status(self):
        """Validate VAT status"""
        vat_status = self.cleaned_data.get('vat_status')
        
        if not vat_status:
            raise ValidationError('VAT status is required.', code='required')
        
        valid_choices = [choice[0] for choice in Supplier.CATEGORY_CHOICES]
        if vat_status not in valid_choices:
            raise ValidationError('Invalid VAT status selection.', code='invalid_choice')
        
        return vat_status
    
    def clean_philgeps_registration(self):
        """Validate PhilGEPS registration (optional)"""
        philgeps = self.cleaned_data.get('philgeps_registration', '').strip()
        
        if not philgeps:
            return ''
        
        if len(philgeps) > 100:
            raise ValidationError('PhilGEPS registration must not exceed 100 characters.', code='max_length')
        
        try:
            validate_alphanumeric_with_spaces(philgeps)
        except ValidationError:
            raise ValidationError(
                'PhilGEPS registration must contain only letters, numbers, spaces, hyphens, and periods.',
                code='invalid_chars'
            )
        
        return sanitize_string_input(philgeps)
    
    def clean_address(self):
        """Validate address"""
        address = self.cleaned_data.get('address', '').strip()
        
        if not address:
            raise ValidationError('Address is required.', code='required')
        
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
        """Validate proprietor name"""
        proprietor = self.cleaned_data.get('propprietor', '').strip()
        
        if not proprietor:
            raise ValidationError('Proprietor/Owner name is required.', code='required')
        
        if len(proprietor) < 2:
            raise ValidationError('Proprietor name must be at least 2 characters long.', code='min_length')
        
        if len(proprietor) > 200:
            raise ValidationError('Proprietor name must not exceed 200 characters.', code='max_length')
        
        try:
            validate_alphanumeric_with_spaces(proprietor)
        except ValidationError:
            raise ValidationError(
                'Proprietor name must contain only letters, numbers, spaces, hyphens, and periods.',
                code='invalid_chars'
            )
        
        try:
            validate_no_script_content(proprietor)
        except ValidationError:
            raise ValidationError('Proprietor name contains invalid content.', code='script_injection')
        
        return sanitize_string_input(proprietor)
    
    def clean_contact_number(self):
        """Validate contact number"""
        contact = self.cleaned_data.get('contact_number', '').strip()
        
        if not contact:
            raise ValidationError('Contact number is required.', code='required')
        
        try:
            validate_phone_number(contact)
        except ValidationError:
            raise ValidationError(
                'Please enter a valid Philippine phone number.',
                code='invalid_format'
            )
        
        return contact
