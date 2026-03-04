"""Location Models - districts and Negosyo Centers"""

from django.db import models
from django.core.exceptions import ValidationError
from dashboard_app.validators import (
    sanitize_string_input,
    validate_no_script_content,
)


class District(models.Model):
    """Districts for Negosyo Center organization"""
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="District name (e.g., District 1, District 2)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the district"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this district active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "District"
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate district data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'District name must be at least 2 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = District.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A district with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class NegosyoCenter(models.Model):
    """Negosyo Centers organized by district"""
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='negosyo_centers',
        help_text="Parent district"
    )
    name = models.CharField(
        max_length=100,
        help_text="Negosyo Center name"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for the NC (e.g., sto_domingo)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the NC"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this NC active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district__order', 'district__name', 'name']
        verbose_name = "Negosyo Center"
        verbose_name_plural = "Negosyo Centers"
        unique_together = ('district', 'code')

    def __str__(self):
        return f"{self.name} ({self.district.name})"
    
    def clean(self):
        """Validate negosyo center data"""
        self.name = sanitize_string_input(self.name)
        self.code = self.code.lower().strip()
        validate_no_script_content(self.name)
        
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError({'name': 'NC name must be at least 2 characters.'})
        
        if not self.code or len(self.code.strip()) < 2:
            raise ValidationError({'code': 'NC code must be at least 2 characters.'})
        
        # Check uniqueness on update
        if self.id:
            duplicate = NegosyoCenter.objects.filter(
                code__iexact=self.code
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'code': 'A NC with this code already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
