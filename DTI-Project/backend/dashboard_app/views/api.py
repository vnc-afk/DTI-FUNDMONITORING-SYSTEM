"""API Views - Helper functions for AJAX requests and data retrieval"""

import re
from decimal import Decimal

from django.db.models import Sum
from django.http import JsonResponse
from django.utils.timezone import now

from bank_statement_app.models import BankStatement
from dashboard_app.utils.decorators import api_login_required
from data_management_app.models import (
    BreakdownCategory,
    FundSource,
    FundSourceBreakdown,
    Supplier,
    TaxTable,
)
from mater_fundmonitor_app.models import MasterFundMonitoring


def get_supplier_data(request, supplier_id):
    """API endpoint to get supplier TIN and VAT status for auto-population"""
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        data = {
            "tin": supplier.tin,
            "vat_status": supplier.vat_status,
        }
        return JsonResponse(data)
    except Supplier.DoesNotExist:
        return JsonResponse({"error": "Supplier not found"}, status=404)


def parse_tax_rate(value):
    """
    Parse tax rate value - can be:
    - A formula string like "=0.05/1.12"
    - A numeric string like "0.05"
    - An empty string or None
    """
    if value is None or value == "":
        return None

    value = str(value).strip()

    if not value:
        return None

    # Check if it's a formula (starts with =)
    if value.startswith("="):
        try:
            # Remove the = sign and evaluate
            formula = value[1:]
            # Sanitize - only allow numbers, operators, parentheses, decimal points
            if not re.match(r"^[0-9+\-*/%().\s]+$", formula):
                return None
            # Safely evaluate the formula
            result = float(eval(formula))
            return result
        except (ValueError, TypeError, SyntaxError):
            return None
    else:
        # Try to convert directly to float
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def get_tax_rates(request, purchase_type_id):
    """API endpoint to get tax rates for a specific purchase type"""
    try:
        # Validate that purchase_type_id is provided and is a valid integer
        if not purchase_type_id:
            return JsonResponse(
                {"error": "Purchase type ID is required", "status": "error"}, status=400
            )

        def build_payload(entry):
            vat_goods_5 = parse_tax_rate(entry.vat_goods_5) if entry else None
            vat_services_5 = parse_tax_rate(entry.vat_services_5) if entry else None
            vat_goods_services_3 = (
                parse_tax_rate(entry.vat_goods_services_3) if entry else None
            )
            vat_goods_1 = parse_tax_rate(entry.vat_goods_1) if entry else None
            vat_services_2 = parse_tax_rate(entry.vat_services_2) if entry else None
            vat_rental_5 = parse_tax_rate(entry.vat_rental_5) if entry else None
            vat_prof_fee_10 = parse_tax_rate(entry.vat_prof_fee_10) if entry else None

            # The Master Fund Monitoring form expects these keys.
            payload = {
                "configured": bool(entry),
                "goods_5_percent": vat_goods_5,
                "services_5_percent": vat_services_5,
                "goods_services_3_percent": vat_goods_services_3,
                "goods_1_percent": vat_goods_1,
                "services_2_percent": vat_services_2,
                "rental_5_percent": vat_rental_5,
                "prof_fee_10_percent": vat_prof_fee_10,
                # Backwards-compatible keys (used by older clients/pages).
                "vat_goods_5": vat_goods_5,
                "vat_services_5": vat_services_5,
                "vat_goods_services_3": vat_goods_services_3,
                "vat_goods_1": vat_goods_1,
                "vat_services_2": vat_services_2,
                "vat_rental_5": vat_rental_5,
                "vat_prof_fee_10": vat_prof_fee_10,
            }

            return payload

        tax_entry = TaxTable.objects.filter(purchase_type_id=purchase_type_id).first()
        return JsonResponse(build_payload(tax_entry))
    except TaxTable.DoesNotExist:
        # Defensive: we now use .filter().first(), so this block should not run.
        return JsonResponse({"configured": False}, status=200)
    except Exception as e:
        return JsonResponse(
            {"error": f"Error retrieving tax rates: {str(e)}", "status": "error"},
            status=500,
        )


def get_fund_budget(request):
    """API endpoint to get budget information for a fund source"""
    fund_id = request.GET.get("fund_id")

    if not fund_id:
        return JsonResponse({"error": "Fund ID is required"}, status=400)

    try:
        fund = FundSource.objects.get(pk=fund_id)

        # Calculate total disbursements for this fund
        total_disbursed = (
            MasterFundMonitoring.objects.filter(
                fund_source=fund, transaction_type="Disbursement"
            ).aggregate(total=Sum("payments"))["total"]
            or 0
        )

        # Calculate total refunds for this fund (refunds reduce the net disbursed amount)
        total_refunded = (
            MasterFundMonitoring.objects.filter(
                fund_source=fund, transaction_type="Refund"
            ).aggregate(total=Sum("payments"))["total"]
            or 0
        )

        # Calculate total downloads (fund allocations from higher office via MDP)
        total_downloads = (
            MasterFundMonitoring.objects.filter(fund_source=fund).aggregate(
                total=Sum("downloads")
            )["total"]
            or 0
        )

        # Net disbursed = disbursements minus refunds
        net_disbursed = total_disbursed - total_refunded

        # Total available = annual budget + downloads - net disbursed
        total_available = (fund.annual_budget or 0) + total_downloads
        available = total_available - net_disbursed

        data = {
            "id": fund.id,
            "name": fund.name,
            "annual_budget": float(fund.annual_budget or 0),
            "total_downloads": float(total_downloads),
            "total_available": float(total_available),
            "total_disbursed": float(total_disbursed),
            "total_refunded": float(total_refunded),
            "net_disbursed": float(net_disbursed),
            "available": float(available),
        }
        return JsonResponse(data)
    except FundSource.DoesNotExist:
        return JsonResponse({"error": "Fund source not found"}, status=404)


def get_mooe_budget(request):
    """API endpoint to get budget information for a MOOE category"""
    mooe_id = request.GET.get("mooe_id")

    if not mooe_id:
        return JsonResponse({"error": "MOOE ID is required"}, status=400)

    try:
        mooe = BreakdownCategory.objects.get(pk=mooe_id)

        # Calculate annual budget for this MOOE category (sum of all fund source breakdowns)
        annual_budget = (
            FundSourceBreakdown.objects.filter(category=mooe).aggregate(
                total=Sum("budget_amount")
            )["total"]
            or 0
        )

        # Calculate total disbursements for this MOOE category
        total_disbursed = (
            MasterFundMonitoring.objects.filter(
                mooe=mooe.code, transaction_type="Disbursement"
            ).aggregate(total=Sum("payments"))["total"]
            or 0
        )

        # Calculate total refunds for this MOOE category (refunds reduce the net disbursed amount)
        total_refunded = (
            MasterFundMonitoring.objects.filter(
                mooe=mooe.code, transaction_type="Refund"
            ).aggregate(total=Sum("payments"))["total"]
            or 0
        )

        # Calculate total downloads for this MOOE category
        total_downloads = (
            MasterFundMonitoring.objects.filter(mooe=mooe.code).aggregate(
                total=Sum("downloads")
            )["total"]
            or 0
        )

        # Net disbursed = disbursements minus refunds
        net_disbursed = total_disbursed - total_refunded

        # Total available = annual budget + downloads - net disbursed
        total_available = annual_budget + total_downloads
        available = total_available - net_disbursed

        data = {
            "id": mooe.id,
            "code": mooe.code,
            "name": mooe.name,
            "annual_budget": float(annual_budget),
            "total_downloads": float(total_downloads),
            "total_available": float(total_available),
            "total_disbursed": float(total_disbursed),
            "total_refunded": float(total_refunded),
            "net_disbursed": float(net_disbursed),
            "available": float(available),
        }
        return JsonResponse(data)
    except BreakdownCategory.DoesNotExist:
        return JsonResponse({"error": "MOOE category not found"}, status=404)


# ============================================================================
# DASHBOARD DATA API ENDPOINTS - For AJAX loading without full page reload
# ============================================================================



@api_login_required
def get_dashboard_kpis(request):
    """
    API endpoint to get dashboard KPI data without rendering full page
    Returns: JSON with KPI summary cards data
    """
    # Get filter parameters from request
    filters = {}
    year = request.GET.get("year")
    filters["date__year"] = int(year) if year and year.isdigit() else now().year

    if request.GET.get("fund_source"):
        filters["fund_source_id"] = request.GET.get("fund_source")
    if request.GET.get("division"):
        filters["division_id"] = request.GET.get("division")
    if request.GET.get("district"):
        filters["nc__district_id"] = request.GET.get("district")
    if request.GET.get("expense_class"):
        filters["expense_classification_id"] = request.GET.get("expense_class")
    if request.GET.get("supplier"):
        filters["payee_id"] = request.GET.get("supplier")
    if request.GET.get("date_month") and str(request.GET.get("date_month")).isdigit():
        filters["date__month"] = int(request.GET.get("date_month"))

    transaction_qs = MasterFundMonitoring.objects.filter(**filters)

    total_budget = FundSource.objects.aggregate(total=Sum("annual_budget"))[
        "total"
    ] or Decimal(0)
    all_fund_sources = FundSource.objects.all()
    active_funds = all_fund_sources.filter(annual_budget__gt=0)

    disbursement_qs = transaction_qs.filter(transaction_type="Disbursement")
    total_disbursement = disbursement_qs.aggregate(total=Sum("payments"))[
        "total"
    ] or Decimal(0)

    downloads_qs = transaction_qs.filter(transaction_type="Downloads")
    total_downloads = downloads_qs.aggregate(total=Sum("payments"))["total"] or Decimal(
        0
    )

    refund_qs = transaction_qs.filter(transaction_type="Refund")
    total_refunds = refund_qs.aggregate(total=Sum("payments"))["total"] or Decimal(0)

    adjustment_qs = transaction_qs.filter(transaction_type="Adjustment")
    total_adjustments = adjustment_qs.aggregate(total=Sum("payments"))[
        "total"
    ] or Decimal(0)

    remaining_balance = (
        total_budget
        - total_disbursement
        - total_downloads
        - total_adjustments
        + total_refunds
    )
    net_disbursement = (
        total_disbursement + total_downloads + total_adjustments - total_refunds
    )
    budget_util_rate = (
        (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    )

    return JsonResponse(
        {
            "totalBudget": float(total_budget),
            "activeFunds": active_funds.count(),
            "activeBudget": float(
                active_funds.aggregate(total=Sum("annual_budget"))["total"] or 0
            ),
            "totalDisbursement": float(total_disbursement),
            "totalDownloads": float(total_downloads),
            "totalRefunds": float(total_refunds),
            "totalAdjustments": float(total_adjustments),
            "remainingBalance": float(remaining_balance),
            "budgetUtilizationRate": budget_util_rate,
            "totalTransactions": transaction_qs.count(),
            "totalSuppliersPaid": transaction_qs.values("payee").distinct().count(),
        }
    )


@api_login_required
def get_dashboard_charts(request):
    """
    API endpoint to get all dashboard chart data
    Returns: JSON with all chart data (monthly trends, fund breakdown, etc.)
    """
    from django.db.models import Count

    # Get filter parameters
    filters = {}
    year = request.GET.get("year")
    filters["date__year"] = int(year) if year and year.isdigit() else now().year

    if request.GET.get("fund_source"):
        filters["fund_source_id"] = request.GET.get("fund_source")
    if request.GET.get("division"):
        filters["division_id"] = request.GET.get("division")
    if request.GET.get("district"):
        filters["nc__district_id"] = request.GET.get("district")
    if request.GET.get("expense_class"):
        filters["expense_classification_id"] = request.GET.get("expense_class")
    if request.GET.get("supplier"):
        filters["payee_id"] = request.GET.get("supplier")
    if request.GET.get("date_month") and str(request.GET.get("date_month")).isdigit():
        filters["date__month"] = int(request.GET.get("date_month"))

    transaction_qs = MasterFundMonitoring.objects.filter(**filters)

    # Monthly trends
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthly_data = {}
    monthly_downloads = {}
    for month in range(1, 13):
        month_sum = transaction_qs.filter(
            date__month=month,
            transaction_type__in=["Disbursement", "Downloads", "Adjustment"],
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
        monthly_data[month_names[month - 1]] = float(month_sum)

        month_downloads = transaction_qs.filter(date__month=month).aggregate(
            total=Sum("downloads")
        )["total"] or Decimal(0)
        monthly_downloads[month_names[month - 1]] = float(month_downloads)

    # Fund source breakdown
    fund_remaining = []
    for fs in FundSource.objects.all():
        disbursed = transaction_qs.filter(
            fund_source=fs,
            transaction_type__in=["Disbursement", "Downloads", "Adjustment"],
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
        refunded = transaction_qs.filter(
            fund_source=fs, transaction_type="Refund"
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
        downloads_amt = transaction_qs.filter(fund_source=fs).aggregate(
            total=Sum("downloads")
        )["total"] or Decimal(0)
        net_disbursed = disbursed - refunded
        remaining = fs.annual_budget + downloads_amt - net_disbursed
        if remaining > 0:
            fund_remaining.append({"name": fs.name, "remaining": float(remaining)})

    fund_remaining.sort(key=lambda x: x["remaining"], reverse=True)

    fund_labels = [item["name"] for item in fund_remaining]
    fund_values = [item["remaining"] for item in fund_remaining]

    # Budget vs disbursement
    budget_vs_disburse = []
    for fs in FundSource.objects.all():
        disburse = transaction_qs.filter(
            fund_source=fs, transaction_type__in=["Disbursement", "Adjustment"]
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

        refund = transaction_qs.filter(
            fund_source=fs, transaction_type="Refund"
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

        net_disbursed = disburse - refund

        budget_vs_disburse.append(
            {
                "name": fs.name,
                "budget": float(fs.annual_budget or 0),
                "disbursed": float(net_disbursed),
            }
        )

    budget_labels = [item["name"] for item in budget_vs_disburse]
    budget_amounts = [item["budget"] for item in budget_vs_disburse]
    disburse_amounts = [item["disbursed"] for item in budget_vs_disburse]

    # Account title / expense object analysis
    expense_analysis = (
        transaction_qs.filter(account_title__isnull=False)
        .values("account_title__name")
        .annotate(total=Sum("payments"))
        .order_by("-total")[:10]
    )

    expense_labels = [item["account_title__name"] for item in expense_analysis]
    expense_values = [float(item["total"] or 0) for item in expense_analysis]

    # Top suppliers / payees
    top_suppliers = (
        transaction_qs.filter(payee__supplier__isnull=False)
        .values("payee__supplier")
        .annotate(total=Sum("payments"))
        .order_by("-total")[:10]
    )

    supplier_labels = [item["payee__supplier"] for item in top_suppliers]
    supplier_values = [float(item["total"] or 0) for item in top_suppliers]

    # MOOE breakdown remaining balance
    mooe_remaining = []
    all_categories = BreakdownCategory.objects.filter(is_active=True).order_by("order")
    for category in all_categories:
        mooe_code = category.code

        mooe_disbursed = transaction_qs.filter(
            mooe=mooe_code,
            transaction_type__in=["Disbursement", "Downloads", "Adjustment"],
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

        mooe_refunded = transaction_qs.filter(
            mooe=mooe_code, transaction_type="Refund"
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

        mooe_downloads = transaction_qs.filter(mooe=mooe_code).aggregate(
            total=Sum("downloads")
        )["total"] or Decimal(0)

        mooe_budget = FundSourceBreakdown.objects.filter(
            category__code=mooe_code
        ).aggregate(total=Sum("budget_amount"))["total"] or Decimal(0)

        net_mooe_disbursed = mooe_disbursed - mooe_refunded
        remaining = mooe_budget + mooe_downloads - net_mooe_disbursed

        mooe_remaining.append(
            {
                "name": category.name or mooe_code,
                "remaining": float(remaining),
            }
        )

    mooe_remaining.sort(key=lambda x: x["remaining"], reverse=True)
    mooe_labels = [item["name"] for item in mooe_remaining]
    mooe_values = [item["remaining"] for item in mooe_remaining]

    # Cheque monitoring
    cheque_status = (
        transaction_qs.filter(cheque_status__isnull=False)
        .values("cheque_status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    cheque_labels = [item["cheque_status"] for item in cheque_status]
    cheque_counts = [item["count"] for item in cheque_status]

    # District spending
    district_spending = (
        transaction_qs.filter(nc__district__isnull=False)
        .values("nc__district__name")
        .annotate(total=Sum("payments"))
        .order_by("-total")
    )

    district_labels = [item["nc__district__name"] for item in district_spending]
    district_values = [float(item["total"] or 0) for item in district_spending]

    # Bank balance trend (year-based)
    selected_year = int(year) if year and str(year).isdigit() else now().year
    bank_statements = BankStatement.objects.filter(date__year=selected_year).order_by(
        "date"
    )

    bank_dates = [str(stmt.date) for stmt in bank_statements]
    bank_debits = [float(stmt.debit or 0) for stmt in bank_statements]
    bank_credits = [float(stmt.credit or 0) for stmt in bank_statements]
    bank_balances = [float(stmt.balance or 0) for stmt in bank_statements]

    return JsonResponse(
        {
            "monthlyData": monthly_data,
            "monthlyDownloads": monthly_downloads,
            "fundLabels": fund_labels,
            "fundBreakdown": fund_labels,
            "fundValues": fund_values,
            "budgetLabels": budget_labels,
            "budgetAmounts": budget_amounts,
            "disburseAmounts": disburse_amounts,
            "expenseLabels": expense_labels,
            "expenseValues": expense_values,
            "supplierLabels": supplier_labels,
            "supplierValues": supplier_values,
            "mooeLabels": mooe_labels,
            "mooeValues": mooe_values,
            "chequeLabels": cheque_labels,
            "chequeCounts": cheque_counts,
            "districtLabels": district_labels,
            "districtValues": district_values,
            "bankDates": bank_dates,
            "bankDebits": bank_debits,
            "bankCredits": bank_credits,
            "bankBalances": bank_balances,
        }
    )


@api_login_required
def get_dashboard_filters(request):
    """
    API endpoint to get available filter options
    Returns: JSON with all filter dropdown options
    """
    from data_management_app.models import District, Division, ExpenseCategory

    years = sorted(
        {
            int(year)
            for year in MasterFundMonitoring.objects.filter(
                date__isnull=False
            ).values_list("date__year", flat=True)
            if year is not None
        },
        reverse=True,
    )

    return JsonResponse(
        {
            "years": years,
            "fundSources": [
                {"id": fs.id, "name": fs.name} for fs in FundSource.objects.all()
            ],
            "divisions": [{"id": d.id, "name": d.name} for d in Division.objects.all()],
            "districts": [{"id": d.id, "name": d.name} for d in District.objects.all()],
            "expenseCategories": [
                {"id": ec.id, "name": ec.name} for ec in ExpenseCategory.objects.all()
            ],
            "suppliers": [
                {"id": s.id, "name": s.supplier}
                for s in Supplier.objects.all().order_by("supplier")[:1000]
            ],
        }
    )


def _get_executive_year(request):
    year_value = request.GET.get("year")
    if year_value and str(year_value).isdigit():
        return int(year_value)
    return now().year


def _get_executive_years():
    years = {
        int(year)
        for year in MasterFundMonitoring.objects.filter(date__isnull=False).values_list(
            "date__year", flat=True
        )
        if year is not None
    }
    years.add(now().year)
    return sorted(years, reverse=True)


def _get_executive_transactions(year):
    return MasterFundMonitoring.objects.filter(date__year=year)


def _format_php_amount(value):
    return f"₱{float(value or 0):,.2f}"


def _build_executive_kpis(transaction_qs):
    total_budget = FundSource.objects.aggregate(total=Sum("annual_budget"))[
        "total"
    ] or Decimal(0)

    total_disbursement = transaction_qs.filter(
        transaction_type="Disbursement"
    ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
    total_downloads = transaction_qs.filter(transaction_type="Downloads").aggregate(
        total=Sum("payments")
    )["total"] or Decimal(0)
    total_refunds = transaction_qs.filter(transaction_type="Refund").aggregate(
        total=Sum("payments")
    )["total"] or Decimal(0)
    total_adjustments = transaction_qs.filter(transaction_type="Adjustment").aggregate(
        total=Sum("payments")
    )["total"] or Decimal(0)

    net_disbursement = (
        total_disbursement + total_downloads + total_adjustments - total_refunds
    )
    remaining_balance = total_budget - net_disbursement
    budget_utilization_pct = (
        (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    )

    if budget_utilization_pct > 100:
        status_label = "Over budget"
        status_color = "#dc2626"
    elif budget_utilization_pct >= 80:
        status_label = "Budget nearing limit"
        status_color = "#d97706"
    else:
        status_label = "Normal budget utilization"
        status_color = "#059669"

    return {
        "total_budget": float(total_budget),
        "total_disbursement": float(total_disbursement),
        "total_downloads": float(total_downloads),
        "total_refunds": float(total_refunds),
        "total_adjustments": float(total_adjustments),
        "net_disbursement": float(net_disbursement),
        "remaining_balance": float(remaining_balance),
        "budget_utilization_pct": budget_utilization_pct,
        "status_label": status_label,
        "status_color": status_color,
        "total_transactions": transaction_qs.count(),
    }


def _build_executive_funds(transaction_qs):
    funds = []

    for fund in FundSource.objects.all():
        spent = transaction_qs.filter(
            fund_source=fund,
            transaction_type__in=["Disbursement", "Downloads", "Adjustment"],
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
        refunded = transaction_qs.filter(
            fund_source=fund,
            transaction_type="Refund",
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

        budget = Decimal(str(fund.annual_budget or 0))
        net_spent = spent - refunded
        remaining = budget - net_spent
        utilization = (float(net_spent) / float(budget) * 100) if budget > 0 else 0

        if utilization > 100:
            status = "Critical"
        elif utilization >= 80:
            status = "Warning"
        else:
            status = "Healthy"

        funds.append(
            {
                "id": fund.id,
                "name": fund.name,
                "budget": float(budget),
                "spent": float(net_spent),
                "remaining": float(remaining),
                "utilization": round(utilization, 1),
                "status": status,
            }
        )

    return funds


def _build_executive_monthly_spendings(transaction_qs):
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthly_spendings = {}

    for month_index, month_name in enumerate(month_names, start=1):
        month_total = transaction_qs.filter(
            date__month=month_index,
            transaction_type__in=["Disbursement", "Downloads", "Adjustment"],
        ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
        monthly_spendings[month_name] = float(month_total)

    return monthly_spendings


def _build_executive_performance_metrics(transaction_qs, monthly_spendings):
    total_downloads = transaction_qs.filter(transaction_type="Downloads").aggregate(
        total=Sum("payments")
    )["total"] or Decimal(0)
    total_monthly_spending = sum(monthly_spendings.values()) if monthly_spendings else 0
    total_transactions = transaction_qs.count()

    return {
        "total_transactions": total_transactions,
        "total_downloads": float(total_downloads),
        "avg_monthly_spending": (
            float(total_monthly_spending) / 12 if monthly_spendings else 0
        ),
        "monthly_transaction_avg": (
            float(total_transactions) / 12 if total_transactions else 0
        ),
    }


def _build_executive_alerts(kpis, funds):
    alerts = []
    utilization = kpis["budget_utilization_pct"]

    if utilization > 100:
        alerts.append(
            {
                "type": "danger",
                "icon": "exclamation-octagon",
                "title": "Budget limit reached",
                "message": (
                    f"Overall budget utilization is {utilization:.1f}% with a remaining balance of "
                    f"{_format_php_amount(kpis['remaining_balance'])}."
                ),
            }
        )
    elif utilization >= 80:
        alerts.append(
            {
                "type": "warning",
                "icon": "exclamation-triangle",
                "title": "Budget nearing limit",
                "message": (
                    f"Overall budget utilization is {utilization:.1f}% and the remaining balance is "
                    f"{_format_php_amount(kpis['remaining_balance'])}."
                ),
            }
        )

    for fund in funds:
        if fund["status"] == "Critical":
            alerts.append(
                {
                    "type": "danger",
                    "icon": "exclamation-octagon",
                    "title": f"{fund['name']} is over budget",
                    "message": (
                        f"{fund['name']} has reached {fund['utilization']:.1f}% utilization and is "
                        f"over budget by {_format_php_amount(abs(fund['remaining']))}."
                    ),
                }
            )
        elif fund["status"] == "Warning":
            alerts.append(
                {
                    "type": "warning",
                    "icon": "exclamation-triangle",
                    "title": f"{fund['name']} needs attention",
                    "message": (
                        f"{fund['name']} is at {fund['utilization']:.1f}% utilization with "
                        f"{_format_php_amount(fund['remaining'])} remaining."
                    ),
                }
            )

    if not alerts:
        alerts.append(
            {
                "type": "info",
                "icon": "check-circle",
                "title": "All Clear",
                "message": "No critical alerts detected. Budget status is healthy.",
            }
        )

    return alerts


@api_login_required
def get_executive_dashboard_kpis(request):
    year = _get_executive_year(request)
    kpis = _build_executive_kpis(_get_executive_transactions(year))
    return JsonResponse(
        {
            "total_budget": kpis["total_budget"],
            "net_disbursement": kpis["net_disbursement"],
            "remaining_balance": kpis["remaining_balance"],
            "budget_utilization_pct": kpis["budget_utilization_pct"],
            "status_label": kpis["status_label"],
            "status_color": kpis["status_color"],
        }
    )


@api_login_required
def get_executive_fund_status(request):
    year = _get_executive_year(request)
    funds = _build_executive_funds(_get_executive_transactions(year))
    return JsonResponse(funds, safe=False)


@api_login_required
def get_executive_performance_metrics(request):
    year = _get_executive_year(request)
    transaction_qs = _get_executive_transactions(year)
    monthly_spendings = _build_executive_monthly_spendings(transaction_qs)
    return JsonResponse(
        _build_executive_performance_metrics(transaction_qs, monthly_spendings)
    )


@api_login_required
def get_executive_monthly_spendings(request):
    year = _get_executive_year(request)
    monthly_spendings = _build_executive_monthly_spendings(
        _get_executive_transactions(year)
    )
    return JsonResponse(monthly_spendings)


@api_login_required
def get_executive_alerts(request):
    year = _get_executive_year(request)
    transaction_qs = _get_executive_transactions(year)
    kpis = _build_executive_kpis(transaction_qs)
    funds = _build_executive_funds(transaction_qs)
    return JsonResponse(_build_executive_alerts(kpis, funds), safe=False)


@api_login_required
def get_executive_available_years(request):
    return JsonResponse(_get_executive_years(), safe=False)
