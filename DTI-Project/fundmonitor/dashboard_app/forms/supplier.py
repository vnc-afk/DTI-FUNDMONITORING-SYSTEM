from django import forms
from dashboard_app.models import Supplier


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
