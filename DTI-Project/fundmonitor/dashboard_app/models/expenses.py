"""Expense Models - expense objects and categories"""

from django.db import models
from django.core.exceptions import ValidationError
from dashboard_app.validators import (
    validate_string_length,
    validate_numeric_only,
    validate_hex_color,
    sanitize_string_input,
    validate_no_script_content,
)


class ExpenseObject(models.Model):
    """Expense objects with account codes"""
    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            validate_string_length(min_length=5, max_length=50),
            validate_numeric_only,
        ],
        help_text="Numeric account code (e.g., '5020101000')"
    )
    name = models.CharField(
        max_length=255,
        validators=[validate_string_length(min_length=3, max_length=255)],
        help_text="Description of expense object"
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        validators=[validate_hex_color],
        help_text="Hex color for display (#RRGGBB)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[validate_string_length(max_length=500)],
        help_text="Additional details"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = "Expense Object"
        verbose_name_plural = "Expense Objects"

    def __str__(self):
        return f"({self.code}) {self.name}"
    
    def clean(self):
        """Validate expense object data"""
        self.name = sanitize_string_input(self.name)
        if self.description:
            self.description = sanitize_string_input(self.description)
        
        validate_no_script_content(self.name)
        if self.description:
            validate_no_script_content(self.description)
        
        # Check uniqueness for code on update
        if self.id:
            duplicate = ExpenseObject.objects.filter(
                code=self.code
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'code': 'This expense code is already in use.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ExpenseCategory(models.Model):
    """Expense categories for classification"""
    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_string_length(min_length=2, max_length=255)],
        help_text="Category name"
    )
    color = models.CharField(
        max_length=7,
        default='#95a5a6',
        validators=[validate_hex_color],
        help_text="Hex color for display (#RRGGBB)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        validators=[validate_string_length(max_length=500)],
        help_text="Category description"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate expense category data"""
        self.name = sanitize_string_input(self.name)
        if self.description:
            self.description = sanitize_string_input(self.description)
        
        validate_no_script_content(self.name)
        if self.description:
            validate_no_script_content(self.description)
        
        # Check uniqueness for name on update
        if self.id:
            duplicate = ExpenseCategory.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A category with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
