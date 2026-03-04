"""Fund Source Models - budget allocation and breakdown management"""

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from dashboard_app.validators import (
    validate_budget_amount,
    validate_transaction_amount,
    validate_string_length,
    sanitize_string_input,
    validate_no_script_content,
)


class FundSource(models.Model):
    """Fund sources for budget allocation"""
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            validate_string_length(min_length=2, max_length=100),
        ],
        help_text="Fund source name"
    )
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[validate_budget_amount],
        help_text="Annual budget allocation"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Fund Source"
        verbose_name_plural = "Fund Sources"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate fund source data"""
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        
        # Check uniqueness on update
        if self.id:
            duplicate = FundSource.objects.filter(
                name__iexact=self.name
            ).exclude(id=self.id).exists()
            if duplicate:
                raise ValidationError({'name': 'A fund source with this name already exists.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class FundSourceBreakdown(models.Model):
    """Breakdown of fund sources by predefined categories"""
    
    fund_source = models.ForeignKey(
        FundSource,
        on_delete=models.CASCADE,
        related_name='breakdowns',
        help_text="Associated fund source"
    )
    category = models.ForeignKey(
        'BreakdownCategory',
        on_delete=models.CASCADE,
        related_name='fund_breakdowns',
        blank=True,
        null=True,
        help_text="Breakdown category"
    )
    budget_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[validate_transaction_amount],
        help_text="Budget allocation for this category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fund_source', 'category__order', 'category__code']
        verbose_name = "Fund Source Breakdown"
        verbose_name_plural = "Fund Source Breakdowns"
        unique_together = ('fund_source', 'category')

    def __str__(self):
        return f"{self.fund_source.name} - {self.category.code}"
    
    def clean(self):
        """Validate breakdown data"""
        # Only validate if fund_source_id is set
        if not self.fund_source_id or not self.budget_amount:
            return
        
        # Validate budget amount doesn't exceed fund source annual budget
        total_breakdown = FundSourceBreakdown.objects.filter(
            fund_source_id=self.fund_source_id
        ).exclude(id=self.id).aggregate(total=Sum('budget_amount'))['total'] or 0
        
        if total_breakdown + self.budget_amount > self.fund_source.annual_budget:
            raise ValidationError({
                'budget_amount': f'Total breakdown ({total_breakdown + self.budget_amount}) cannot exceed annual budget ({self.fund_source.annual_budget}).'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BreakdownCategory(models.Model):
    """Budget breakdown categories"""
    code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Category code (e.g., OO1, 4.1A)"
    )
    name = models.CharField(
        max_length=255,
        help_text="Category description"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this category active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'code']
        verbose_name = "Breakdown Category"
        verbose_name_plural = "Breakdown Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"
