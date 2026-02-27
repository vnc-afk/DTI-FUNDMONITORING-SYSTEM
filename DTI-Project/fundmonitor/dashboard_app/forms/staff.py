from django import forms
from dashboard_app.models import Staff


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
