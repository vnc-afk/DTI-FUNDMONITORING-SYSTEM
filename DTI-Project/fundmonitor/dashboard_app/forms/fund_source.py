"""Fund Source Forms - FundSourceForm and FundSourceBreakdownForm"""

from django import forms
from django.db.models import Sum
from django.core.exceptions import ValidationError
from dashboard_app.models import FundSource, FundSourceBreakdown
from dashboard_app.validators import (
    validate_transaction_amount,
    validate_budget_amount,
)


class FundSourceForm(forms.ModelForm):
    """Form for creating and editing fund sources"""
    
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
        """Validate total breakdown doesn't exceed annual budget and check for duplicates"""
        cleaned_data = super().clean()
        budget_amount = cleaned_data.get('budget_amount')
        category = cleaned_data.get('category')
        
        if not self.fund_source or budget_amount is None or not category:
            return cleaned_data
        
        # Check for duplicate fund_source + category combination
        query = FundSourceBreakdown.objects.filter(
            fund_source=self.fund_source,
            category=category
        )
        
        # Exclude current instance if editing
        if self.instance and self.instance.pk:
            query = query.exclude(id=self.instance.pk)
        
        if query.exists():
            existing = query.first()
            raise ValidationError(
                f'Category {category.code} is already allocated ₱{existing.budget_amount:,.2f}. Please edit the existing breakdown or select a different category.',
                code='duplicate_breakdown'
            )
        
        # Calculate total breakdown
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
