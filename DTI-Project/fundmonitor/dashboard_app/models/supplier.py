from django.db import models
from django.core.exceptions import ValidationError
from dashboard_app.validators import (
    validate_tin_format,
    validate_phone_number,
    validate_string_length,
    validate_unique_supplier_name,
    sanitize_string_input,
    validate_no_script_content,
    validate_alphanumeric_with_spaces,
)


class Supplier(models.Model):
    """Supplier/Payee information"""

    CATEGORY_CHOICES = [
        ('NV', 'Non-VAT Registered'),
        ('V', 'VAT Registered'),
        ('NA', 'N/A'),
    ]
    
    supplier = models.CharField(
        max_length=200,
        unique=True,
        validators=[
            validate_string_length(min_length=2, max_length=200),
            validate_alphanumeric_with_spaces,
        ],
        help_text="Supplier name (alphanumeric with spaces)"
    )
    tin = models.CharField(
        max_length=50,
        validators=[
            validate_tin_format,
        ],
        help_text="Tax Identification Number (###-###-###-###)"
    )
    vat_status = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        help_text="VAT Registration Status"
    )
    philgeps_registration = models.CharField(
        max_length=100,
        blank=True,
        validators=[validate_alphanumeric_with_spaces],
        help_text="PhilGEPS Registration Code (optional)"
    )
    address = models.TextField(
        validators=[validate_string_length(min_length=5, max_length=500)],
        help_text="Complete business address"
    )
    propprietor = models.CharField(
        max_length=200,
        validators=[
            validate_string_length(min_length=2, max_length=200),
            validate_alphanumeric_with_spaces,
        ],
        help_text="Proprietor/Owner name"
    )
    contact_number = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        help_text="Philippine phone number format"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['supplier']
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.supplier
    
    def clean(self):
        """Validate supplier data"""
        # Sanitize all text fields
        self.supplier = sanitize_string_input(self.supplier)
        self.address = sanitize_string_input(self.address)
        self.propprietor = sanitize_string_input(self.propprietor)
        self.philgeps_registration = sanitize_string_input(self.philgeps_registration)
        
        # Check for script injection
        validate_no_script_content(self.supplier)
        validate_no_script_content(self.address)
        validate_no_script_content(self.propprietor)
        
        # Check uniqueness for supplier name on update
        if self.id:
            duplicate = Supplier.objects.filter(
                supplier__iexact=self.supplier
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'supplier': 'A supplier with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
