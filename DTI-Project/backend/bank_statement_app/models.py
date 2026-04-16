from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from dashboard_app.utils.validators import (
    sanitize_string_input,
    validate_date_not_in_future,
    validate_no_script_content,
    validate_transaction_amount,
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


class BankAccount(models.Model):
    name = models.CharField(max_length=255, unique=True)
    account_number = models.CharField(max_length=50, unique=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.name} ({self.account_number})"

    def clean(self):
        self.name = sanitize_string_input(self.name)
        validate_no_script_content(self.name)
        if not self.name or len(self.name.strip()) < 2:
            raise ValidationError(
                {"name": "Bank account name must be at least 2 characters."}
            )
        if not self.account_number or len(self.account_number.strip()) < 5:
            raise ValidationError(
                {"account_number": "Account number must be at least 5 characters."}
            )
        if self.id:
            duplicate_name = (
                BankAccount.objects.filter(name__iexact=self.name)
                .exclude(id=self.id)
                .exists()
            )
            if duplicate_name:
                raise ValidationError(
                    {"name": "A bank account with this name already exists."}
                )
            duplicate_acc = (
                BankAccount.objects.filter(account_number=self.account_number)
                .exclude(id=self.id)
                .exists()
            )
            if duplicate_acc:
                raise ValidationError(
                    {"account_number": "This account number is already in use."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BankStatement(ArchivableModel):
    CATEGORY_CHOICES = [("Cleared", "Cleared"), ("On Process", "On Process")]
    ARCHIVE_UPDATE_FIELDS = {
        "is_archived",
        "archived_at",
        "archived_by",
        "archive_reason",
    }

    date = models.DateField(validators=[validate_date_not_in_future])
    description = models.CharField(max_length=255)
    check_number = models.CharField(max_length=50, blank=True, default="")
    debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        validators=[validate_transaction_amount],
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="On Process",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "created_at"]
        verbose_name = "Bank Statement"
        verbose_name_plural = "Bank Statements"

    def __str__(self):
        return f"{self.date} - {self.description}"

    def _calculate_balance(self):
        debit = self.debit or 0
        credit = self.credit or 0
        previous_statements = (
            BankStatement.objects.all_with_archived()
            .exclude(id=self.id)
            .order_by("date", "created_at")
        )
        if self.created_at:
            previous_on_date = previous_statements.filter(
                Q(date__lt=self.date)
                | Q(date=self.date, created_at__lt=self.created_at)
            )
        else:
            previous_on_date = previous_statements.filter(date__lte=self.date)
        if not previous_on_date.exists():
            return credit - debit
        last_statement = previous_on_date.last()
        previous_balance = last_statement.balance
        return previous_balance + credit - debit

    def clean(self):
        self.description = sanitize_string_input(self.description)
        validate_no_script_content(self.description)
        debit = self.debit or 0
        credit = self.credit or 0
        if debit > 0 and credit > 0:
            raise ValidationError(
                "Cannot have both debit and credit amounts in the same transaction.",
                code="both_debit_credit",
            )
        if debit == 0 and credit == 0:
            raise ValidationError(
                "At least one of debit or credit must be non-zero.", code="no_amount"
            )
        if self.balance is not None and self.balance < 0:
            raise ValidationError(
                "Balance cannot be negative. Please check the transaction amounts or opening balance.",
                code="negative_balance",
            )

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_field_set = set(update_fields)
            if update_field_set and update_field_set.issubset(
                self.ARCHIVE_UPDATE_FIELDS
            ):
                return super().save(*args, **kwargs)

        first_transaction = (
            BankStatement.objects.all_with_archived()
            .exclude(id=self.id)
            .order_by("date", "created_at")
            .first()
        )
        is_first_transaction = not first_transaction
        if not is_first_transaction and self.created_at:
            is_first_transaction = first_transaction.date > self.date or (
                first_transaction.date == self.date
                and first_transaction.created_at > self.created_at
            )

        if is_first_transaction:
            if self.balance is None:
                self.balance = Decimal(0)
        else:
            self.balance = self._calculate_balance()

        self.full_clean()
        super().save(*args, **kwargs)

        if is_first_transaction:
            subsequent_transactions = (
                BankStatement.objects.all_with_archived()
                .exclude(id=self.id)
                .order_by("date", "created_at")
            )
            for transaction in subsequent_transactions:
                transaction.balance = transaction._calculate_balance()
                super(BankStatement, transaction).save(
                    update_fields=["balance", "updated_at"]
                )
