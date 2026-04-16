from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from dashboard_app.utils.validators import (
    sanitize_string_input,
    validate_check_number_format,
    validate_date_not_in_future,
    validate_mooe_format,
    validate_no_script_content,
    validate_string_length,
    validate_transaction_amount,
)
from data_management_app.models import (
    Division,
    ExpenseCategory,
    ExpenseObject,
    FundSource,
    NegosyoCenter,
    PurchaseType,
    Staff,
    Supplier,
)


class ArchivableQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

    def all_records(self):
        return self.all()


class ArchivableManager(models.Manager):
    def get_queryset(self):
        return ArchivableQuerySet(self.model, using=self._db).active()

    def all_with_archived(self):
        return ArchivableQuerySet(self.model, using=self._db).all()

    def archived(self):
        return self.all_with_archived().archived()


class ArchivableModel(models.Model):
    is_archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    archived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_archived_records",
    )
    archive_reason = models.TextField(blank=True, default="")

    objects = ArchivableManager()

    class Meta:
        abstract = True

    def archive(self, user=None, reason=""):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archive_reason = reason
        self.save(
            update_fields=[
                "is_archived",
                "archived_at",
                "archived_by",
                "archive_reason",
            ]
        )

    def unarchive(self):
        self.is_archived = False
        self.archived_at = None
        self.archived_by = None
        self.archive_reason = ""
        self.save(
            update_fields=[
                "is_archived",
                "archived_at",
                "archived_by",
                "archive_reason",
            ]
        )


class MasterFundMonitoring(ArchivableModel):
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name="monitoring_records",
        null=True,
        blank=True,
    )
    fund_source = models.ForeignKey(
        FundSource,
        on_delete=models.CASCADE,
        related_name="monitoring_records",
        null=True,
        blank=True,
    )
    mooe = models.CharField(
        max_length=100,
        validators=[
            validate_string_length(min_length=2, max_length=100),
            validate_mooe_format,
        ],
        null=True,
        blank=True,
    )
    nc = models.ForeignKey(
        NegosyoCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monitoring_records",
    )
    date = models.DateField(validators=[validate_date_not_in_future])
    payee = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="monitoring_records"
    )
    particulars = models.TextField(
        validators=[validate_string_length(min_length=5, max_length=500)]
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ("Disbursement", "Disbursement"),
            ("Downloads", "Downloads"),
            ("Refund", "Refund"),
            ("Adjustment", "Adjustment"),
        ],
        default="Disbursement",
    )
    tin = models.CharField(max_length=20, blank=True, null=True)
    tax_type = models.CharField(max_length=100, blank=True, null=True)
    purchase_type = models.ForeignKey(
        PurchaseType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="monitoring_records",
    )
    payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    dv_number = models.CharField(max_length=50, blank=True, null=True)
    downloads = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    cheque_number = models.CharField(
        max_length=50, blank=True, null=True, validators=[validate_check_number_format]
    )
    cleared_date = models.DateField(
        blank=True, null=True, validators=[validate_date_not_in_future]
    )
    account_title = models.ForeignKey(
        ExpenseObject,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="monitoring_accounts",
    )
    goods_5_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    services_5_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    goods_services_3_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    goods_1_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    services_2_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    rental_5_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    prof_fee_10_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    expense_classification = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="monitoring_expenses",
    )
    cheque_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Cleared", "Cleared")],
        default="Pending",
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="monitoring_records",
    )
    goods_5_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    services_5_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    goods_services_1_percent = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    goods_1_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    services_2_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    rental_5_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    prof_fee_10_percent_2 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Master Fund Monitoring"
        verbose_name_plural = "Master Fund Monitorings"

    def __str__(self):
        return f"{self.payee.supplier} - {self.date}"

    def clean(self):
        self.particulars = sanitize_string_input(self.particulars)
        validate_no_script_content(self.particulars)
        if self.cleared_date and self.cleared_date < self.date:
            raise ValidationError(
                {
                    "cleared_date": "Cleared date must be on or after the transaction date."
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
