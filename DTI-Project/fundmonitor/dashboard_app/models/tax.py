"""Tax Models - purchase types and tax rate management"""

from django.db import models
from django.core.exceptions import ValidationError
from dashboard_app.validators import (
    validate_string_length,
    validate_no_script_content,
    sanitize_string_input,
)


class PurchaseType(models.Model):
    """Purchase Types for procurement categorization"""
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Purchase type name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this purchase type active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Purchase Type"
        verbose_name_plural = "Purchase Types"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate purchase type data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'Name must be at least 2 characters.'})
        
        if len(self.name) > 100:
            raise ValidationError({'name': 'Name cannot exceed 100 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = PurchaseType.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A purchase type with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TaxTable(models.Model):
    """Entries for the tax lookup table used throughout the system."""

    purchase_type = models.ForeignKey(
        PurchaseType,
        on_delete=models.CASCADE,
        related_name='tax_entries',
        help_text="Purchase type for this tax entry",
        null=True,
        blank=False
    )

    # VAT sub‑categories
    vat_goods_5 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT goods (5%)"
    )
    vat_services_5 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT services (5%)"
    )
    vat_goods_services_3 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT goods & services (3%)"
    )
    vat_goods_1 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT goods (1%)"
    )
    vat_services_2 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT services (2%)"
    )
    vat_rental_5 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT rental (5%)"
    )
    vat_prof_fee_10 = models.CharField(
        max_length=50,
        blank=True,
        help_text="Code/description for VAT professional fee (10%)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['purchase_type__name']
        verbose_name = "Tax Table Entry"
        verbose_name_plural = "Tax Table Entries"
        unique_together = ('purchase_type',)

    def __str__(self):
        return self.purchase_type.name

    def clean(self):
        """Validate tax table entry"""
        from dashboard_app.validators import validate_no_script_content
        
        if not self.purchase_type:
            raise ValidationError({'purchase_type': 'Purchase type is required.'})
        
        validate_no_script_content(self.vat_goods_5 or '')
        validate_no_script_content(self.vat_services_5 or '')
        validate_no_script_content(self.vat_goods_services_3 or '')
        validate_no_script_content(self.vat_goods_1 or '')
        validate_no_script_content(self.vat_services_2 or '')
        validate_no_script_content(self.vat_rental_5 or '')
        validate_no_script_content(self.vat_prof_fee_10 or '')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
