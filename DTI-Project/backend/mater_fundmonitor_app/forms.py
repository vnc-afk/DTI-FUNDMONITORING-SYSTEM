from django import forms
from django.core.exceptions import ValidationError

from dashboard_app.utils.validators import (
    sanitize_string_input,
    validate_check_number_format,
    validate_date_not_in_future,
    validate_dv_number_format,
    validate_no_script_content,
    validate_transaction_amount,
)
from data_management_app.models import (
    BreakdownCategory,
    Division,
    ExpenseCategory,
    ExpenseObject,
    FundSource,
    NegosyoCenter,
    PurchaseType,
    Staff,
    Supplier,
)
from mater_fundmonitor_app.models import MasterFundMonitoring


class MasterFundMonitoringForm(forms.ModelForm):
    """Form for creating and editing master fund monitoring records"""

    payee = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.Select(
            attrs={"class": "form-select", "id": "payeeSelect", "required": True}
        ),
        label="Payee",
    )

    fund_source = forms.ModelChoiceField(
        queryset=FundSource.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Fund Source",
        required=False,
        error_messages={"required": "Please select a Fund Source."},
    )

    mooe = forms.ModelChoiceField(
        queryset=BreakdownCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="MOOE",
        help_text="Maintenance and Other Operating Expenses",
        required=False,
    )

    division = forms.ModelChoiceField(
        queryset=Division.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Division",
        required=False,
    )

    nc = forms.ModelChoiceField(
        queryset=NegosyoCenter.objects.filter(is_active=True).select_related(
            "district"
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="NC",
        required=False,
    )

    account_title = forms.ModelChoiceField(
        queryset=ExpenseObject.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Account Title",
        required=False,
    )

    expense_classification = forms.ModelChoiceField(
        queryset=ExpenseCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Expense Classification",
        required=False,
    )

    staff = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Staff",
        required=False,
    )

    purchase_type = forms.ModelChoiceField(
        queryset=PurchaseType.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select", "id": "purchaseTypeSelect"}),
        label="Purchase Type",
        required=False,
    )

    transaction_type = forms.ChoiceField(
        choices=[
            ("Disbursement", "Disbursement"),
            ("Downloads", "Downloads"),
            ("Refund", "Refund"),
            ("Adjustment", "Adjustment"),
        ],
        widget=forms.RadioSelect(
            attrs={"class": "transaction-type-radio", "id": "transactionTypeRadio"}
        ),
        label="Transaction Type",
        initial="Disbursement",
        help_text="Select whether this is a disbursement, downloads, refund, or adjustment",
    )

    class Meta:
        model = MasterFundMonitoring
        exclude = ["cheque_status"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "class": "form-control has-prefix",
                    "type": "date",
                    "required": True,
                }
            ),
            "particulars": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Transaction details",
                    "required": True,
                }
            ),
            "transaction_type": forms.RadioSelect(
                attrs={"class": "transaction-type-radio"}
            ),
            "tin": forms.TextInput(
                attrs={"class": "form-control", "id": "tinField", "readonly": True}
            ),
            "tax_type": forms.TextInput(
                attrs={"class": "form-control", "id": "taxTypeField", "readonly": True}
            ),
            "payments": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "dv_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "DV number",
                    "maxlength": "50",
                }
            ),
            "downloads": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "cheque_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Check number",
                    "maxlength": "50",
                }
            ),
            "cleared_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "goods_5_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "services_5_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "goods_services_3_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "goods_1_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "services_2_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "rental_5_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "prof_fee_10_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "goods_5_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "services_5_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "goods_services_1_percent": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "goods_1_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "services_2_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "rental_5_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
            "prof_fee_10_percent_2": forms.NumberInput(
                attrs={
                    "class": "form-control has-prefix-text",
                    "step": "0.01",
                    "min": "0",
                    "readonly": True,
                }
            ),
        }

    def clean_mooe(self):
        mooe = self.cleaned_data.get("mooe")
        if not mooe:
            return None
        if hasattr(mooe, "code"):
            return mooe.code
        return mooe

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if not date:
            raise ValidationError("Transaction date is required.", code="required")
        try:
            validate_date_not_in_future(date)
        except ValidationError:
            raise ValidationError(
                "Transaction date cannot be in the future.", code="future_date"
            )
        return date

    def clean_particulars(self):
        particulars = (self.cleaned_data.get("particulars") or "").strip()
        if not particulars:
            raise ValidationError("Particulars is required.", code="required")
        if len(particulars) < 5:
            raise ValidationError(
                "Particulars must be at least 5 characters long.", code="min_length"
            )
        if len(particulars) > 500:
            raise ValidationError(
                "Particulars must not exceed 500 characters.", code="max_length"
            )
        try:
            validate_no_script_content(particulars)
        except ValidationError:
            raise ValidationError(
                "Particulars contains invalid content.", code="script_injection"
            )
        return sanitize_string_input(particulars)

    def clean_payments(self):
        payments = self.cleaned_data.get("payments")
        if payments in (None, ""):
            return 0
        try:
            validate_transaction_amount(payments)
        except ValidationError:
            raise ValidationError(
                "Payments amount must be a positive number.", code="invalid_amount"
            )
        return payments

    def clean_dv_number(self):
        dv_number = (self.cleaned_data.get("dv_number") or "").strip()
        if not dv_number:
            return ""
        try:
            validate_dv_number_format(dv_number)
        except ValidationError:
            raise ValidationError(
                "DV number must contain only letters, numbers, and hyphens.",
                code="invalid_format",
            )
        return dv_number

    def clean_downloads(self):
        downloads = self.cleaned_data.get("downloads")
        if downloads in (None, ""):
            return 0
        try:
            validate_transaction_amount(downloads)
        except ValidationError:
            raise ValidationError(
                "Downloads amount must be a positive number.", code="invalid_amount"
            )
        return downloads

    def clean_cheque_number(self):
        cheque_number = self.cleaned_data.get("cheque_number")
        if not cheque_number:
            return ""
        cheque_number = str(cheque_number).strip()
        if not cheque_number:
            return ""
        try:
            validate_check_number_format(cheque_number)
        except ValidationError:
            raise ValidationError(
                "Cheque number must contain only letters, numbers, and hyphens.",
                code="invalid_format",
            )
        return cheque_number

    def clean_cleared_date(self):
        cleared_date = self.cleaned_data.get("cleared_date")
        if not cleared_date:
            return cleared_date
        try:
            validate_date_not_in_future(cleared_date)
        except ValidationError:
            raise ValidationError(
                "Cleared date cannot be in the future.", code="future_date"
            )
        return cleared_date

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        cleared_date = cleaned_data.get("cleared_date")
        fund_source = cleaned_data.get("fund_source")
        payments = cleaned_data.get("payments")
        transaction_type = cleaned_data.get("transaction_type")

        if date and cleared_date and cleared_date < date:
            raise ValidationError(
                {
                    "cleared_date": "Cleared date must be on or after the transaction date."
                }
            )

        if (
            fund_source
            and payments
            and transaction_type in ["Disbursement", "Downloads"]
        ):
            from decimal import Decimal

            from django.db.models import Sum

            fund_budget = Decimal(str(fund_source.annual_budget or 0))
            total_disbursed = MasterFundMonitoring.objects.filter(
                fund_source=fund_source,
                transaction_type__in=["Disbursement", "Downloads"],
            ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
            total_refunded = MasterFundMonitoring.objects.filter(
                fund_source=fund_source, transaction_type="Refund"
            ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

            if self.instance.pk:
                if self.instance.transaction_type in ["Disbursement", "Downloads"]:
                    total_disbursed -= Decimal(str(self.instance.payments or 0))
                elif self.instance.transaction_type == "Refund":
                    total_refunded -= Decimal(str(self.instance.payments or 0))

            net_disbursed = total_disbursed - total_refunded
            available_budget = fund_budget - net_disbursed
            new_payment = Decimal(str(payments))

            if new_payment > available_budget:
                trans_type = (
                    "payment" if transaction_type == "Disbursement" else "download"
                )
                raise ValidationError(
                    {
                        "payments": f"{transaction_type} exceeds available budget. Fund budget: ₱{fund_budget:,.2f}, "
                        f"Net disbursed (after refunds): ₱{net_disbursed:,.2f}, "
                        f"Available: ₱{available_budget:,.2f}. "
                        f"You are trying to {trans_type} ₱{new_payment:,.2f}."
                    }
                )

        mooe = cleaned_data.get("mooe")
        if mooe and payments and transaction_type in ["Disbursement", "Downloads"]:
            from decimal import Decimal

            from django.db.models import Sum

            from data_management_app.models import FundSourceBreakdown

            mooe_code = mooe.code if hasattr(mooe, "code") else str(mooe)
            mooe_budget = FundSourceBreakdown.objects.filter(
                category__code=mooe_code
            ).aggregate(total=Sum("budget_amount"))["total"] or Decimal(0)
            mooe_disbursed = MasterFundMonitoring.objects.filter(
                mooe=mooe_code, transaction_type__in=["Disbursement", "Downloads"]
            ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
            mooe_refunded = MasterFundMonitoring.objects.filter(
                mooe=mooe_code, transaction_type="Refund"
            ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

            if self.instance.pk:
                if self.instance.transaction_type in ["Disbursement", "Downloads"]:
                    mooe_disbursed -= Decimal(str(self.instance.payments or 0))
                elif self.instance.transaction_type == "Refund":
                    mooe_refunded -= Decimal(str(self.instance.payments or 0))

            mooe_net_disbursed = mooe_disbursed - mooe_refunded
            mooe_available = mooe_budget - mooe_net_disbursed
            new_payment_decimal = Decimal(str(payments))

            if new_payment_decimal > mooe_available:
                raise ValidationError(
                    {
                        "payments": f"Payment exceeds MOOE budget. MOOE budget: ₱{mooe_budget:,.2f}, "
                        f"Net disbursed (after refunds): ₱{mooe_net_disbursed:,.2f}, "
                        f"Available: ₱{mooe_available:,.2f}. "
                        f"You are trying to disburse ₱{new_payment_decimal:,.2f}."
                    }
                )

        return cleaned_data


__all__ = ["MasterFundMonitoringForm"]
