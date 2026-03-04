"""Tax Table Forms - TaxTableForm"""

from django import forms
from django.core.exceptions import ValidationError
from dashboard_app.models import TaxTable, PurchaseType


class TaxTableForm(forms.ModelForm):
    """Form for creating and editing tax table entries"""
    
    purchase_type = forms.ModelChoiceField(
        queryset=PurchaseType.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        help_text="Select a purchase type"
    )
    
    class Meta:
        model = TaxTable
        fields = ['purchase_type', 'vat_goods_5', 'vat_services_5', 'vat_goods_services_3', 
                  'vat_goods_1', 'vat_services_2', 'vat_rental_5', 'vat_prof_fee_10']
        widgets = {
            'purchase_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'vat_goods_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_services_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_goods_services_3': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_goods_1': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_services_2': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_rental_5': forms.TextInput(attrs={'class': 'form-control'}),
            'vat_prof_fee_10': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_purchase_type(self):
        """Validate purchase type selection"""
        purchase_type = self.cleaned_data.get('purchase_type')
        
        if not purchase_type:
            raise ValidationError('Purchase type is required.', code='required')
        
        # Check uniqueness
        queryset = TaxTable.objects.filter(purchase_type=purchase_type)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('A tax entry for this purchase type already exists.', code='unique')
        
        return purchase_type
