from django import forms


class ImportDataForm(forms.Form):
    """Form for importing data from Excel/CSV files"""
    
    DATA_TYPE_CHOICES = [
        ('supplier', 'Suppliers'),
        ('bank_statement', 'Bank Statements'),
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
            # Check file extension
            allowed_extensions = ['.xlsx', '.xls', '.csv']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    'File format not supported. Please upload .xlsx, .xls, or .csv file'
                )
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10MB')
        
        return file
