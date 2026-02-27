from django import forms
from .models import BankStatement, Staff
from .models import Supplier
from .models import FundSource

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'middle_initial', 'last_name', 'division']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., J'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'division': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'tin': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_status': forms.Select(attrs={'class': 'form-select'}), 
            'philgeps_registration': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'propprietor': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FundSourceForm(forms.ModelForm):
    class Meta:
        model = FundSource
        fields = ['name', 'annual_budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BankStatementForm(forms.ModelForm):
    class Meta:
        model = BankStatement
        fields = '__all__'
        widgets = {
            # transaction info
            'date': forms.DateInput(attrs={'class': 'form-control has-prefix', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'check_number': forms.TextInput(attrs={'class': 'form-control has-prefix'}),
            # amounts (use has-prefix-text since prefix is plain currency symbol)
            'debit': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }