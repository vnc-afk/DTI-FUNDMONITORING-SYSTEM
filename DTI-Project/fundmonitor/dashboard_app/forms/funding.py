from django import forms
from dashboard_app.models import FundSource, BankStatement, MasterFundMonitoring, Supplier


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


class MasterFundMonitoringForm(forms.ModelForm):
    # District/NC choices with optgroups
    NC_CHOICES = (
        ('District 1', (
            ('sto_domingo', 'Sto. Domingo'),
            ('bacacay', 'Bacacay'),
            ('malilipot', 'Malilipot'),
            ('tabaco_city', 'Tabaco City'),
            ('tiwi', 'Tiwi'),
        )),
        ('District 2', (
            ('apo', 'APO'),
            ('sedcen', 'SEDCEN'),
            ('camalig', 'Camalig'),
            ('daraga', 'Daraga'),
            ('manito', 'Manito'),
        )),
        ('District 3', (
            ('guinobatan', 'Guinobatan'),
            ('ligao_city', 'Ligao City'),
            ('oas', 'Oas'),
            ('polangui', 'Polangui'),
            ('piodoran', 'Piodoran'),
        )),
    )
    
    # Make payee a dropdown of suppliers
    payee = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'payeeSelect'}),
        label='Payee'
    )
    
    # Make fund_source a dropdown of fund sources
    fund_source = forms.ModelChoiceField(
        queryset=FundSource.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Fund Source'
    )
    
    # Make nc a dropdown with district groups
    nc = forms.ChoiceField(
        choices=NC_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='NC',
        required=True
    )
    
    class Meta:
        model = MasterFundMonitoring
        fields = '__all__'
        widgets = {
            # Transaction Information
            'division': forms.TextInput(attrs={'class': 'form-control'}),
            'mooe': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control has-prefix', 'type': 'date'}),
            'particulars': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # TIN and Tax Information
            'tin': forms.TextInput(attrs={'class': 'form-control', 'id': 'tinField', 'readonly': True}),
            'tax_type': forms.TextInput(attrs={'class': 'form-control', 'id': 'taxTypeField', 'readonly': True}),
            'purchase_type': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Financial Details
            'downloads': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'payments': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'dv_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cheque_number': forms.TextInput(attrs={'class': 'form-control'}),
            'cleared_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'account_title': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Tax Breakdown (First Set)
            'goods_5_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'services_5_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'goods_services_3_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'goods_1_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'services_2_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'rental_5_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'prof_fee_10_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            
            # Additional Information
            'expense_classification': forms.TextInput(attrs={'class': 'form-control'}),
            'cheque_status': forms.Select(attrs={'class': 'form-select'}),
            'staff': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Tax Breakdown (Second Set)
            'goods_5_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'services_5_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'goods_services_1_percent': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'goods_1_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'services_2_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'rental_5_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
            'prof_fee_10_percent_2': forms.NumberInput(attrs={'class': 'form-control has-prefix-text'}),
        }
