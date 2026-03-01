from django import forms
from django.core.exceptions import ValidationError
from dashboard_app.models import Staff
from dashboard_app.validators import (
    validate_letters_only,
    sanitize_string_input,
    validate_no_script_content,
)


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name (letters only)',
                'required': True
            }),
            'middle_initial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., J',
                'maxlength': '5'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name (letters only)',
                'required': True
            }),
            'division': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }
    
    def clean_first_name(self):
        """Validate first name"""
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
            raise ValidationError(
                'First name must contain only letters, spaces, hyphens, periods, and apostrophes.',
                code='invalid_chars'
            )
        
        # Check for script injection
        try:
            validate_no_script_content(first_name)
        except ValidationError:
            raise ValidationError('First name contains invalid content.', code='script_injection')
        
        return sanitize_string_input(first_name)
    
    def clean_middle_initial(self):
        """Validate middle initial"""
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
        """Validate last name"""
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
            raise ValidationError(
                'Last name must contain only letters, spaces, hyphens, periods, and apostrophes.',
                code='invalid_chars'
            )
        
        try:
            validate_no_script_content(last_name)
        except ValidationError:
            raise ValidationError('Last name contains invalid content.', code='script_injection')
        
        return sanitize_string_input(last_name)
    
    def clean_division(self):
        """Validate division"""
        division = self.cleaned_data.get('division')
        
        if not division:
            raise ValidationError('Division is required.', code='required')
        
        return division
    
    def clean(self):
        """Cross-field validations"""
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        
        # Ensure different first and last names
        if first_name and last_name and first_name.lower() == last_name.lower():
            raise ValidationError(
                'First name and last name must be different.',
                code='same_names'
            )
        
        return cleaned_data
