from django.db import models
from django.core.exceptions import ValidationError
from dashboard_app.validators import (
    validate_letters_only,
    validate_unique_division_name,
    validate_string_length,
    sanitize_string_input,
    validate_no_script_content,
)


class Division(models.Model):
    """Division for staff and fund monitoring"""
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_letters_only,
        ],
        help_text="Division name (letters and spaces only)"
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate division data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        # Check uniqueness on update
        if self.id:
            duplicate = Division.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A division with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Staff(models.Model):
    """Staff members in the organization"""
    first_name = models.CharField(
        max_length=100,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_letters_only,
        ],
        help_text="First name (letters, spaces, hyphens, and apostrophes only)"
    )
    middle_initial = models.CharField(
        max_length=5,
        blank=True,
        validators=[validate_letters_only],
        help_text="Middle initial (letters only)"
    )
    last_name = models.CharField(
        max_length=100,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_letters_only,
        ],
        help_text="Last name (letters, spaces, hyphens, and apostrophes only)"
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name='staff_members',
        help_text="Select staff division",
        null=True,
        blank=True 
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Staff"
        verbose_name_plural = "Staff Members"

    def __str__(self):
        middle = f" {self.middle_initial}" if self.middle_initial else ""
        return f"{self.first_name}{middle} {self.last_name}"
    
    def clean(self):
        """Validate staff data"""
        self.first_name = sanitize_string_input(self.first_name)
        self.middle_initial = sanitize_string_input(self.middle_initial)
        self.last_name = sanitize_string_input(self.last_name)
        
        validate_no_script_content(self.first_name)
        validate_no_script_content(self.last_name)
        
        if self.middle_initial:
            validate_no_script_content(self.middle_initial)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

