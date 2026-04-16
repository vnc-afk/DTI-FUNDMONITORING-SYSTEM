"""Report download endpoints for API-first mode."""

import csv
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.utils.timezone import now

from mater_fundmonitor_app.models import MasterFundMonitoring


def download_mooe(request, report_type):
    """Download MOOE report (disbursement or downloads) as CSV."""
    from data_management_app.models import BreakdownCategory

    current_year = now().year
    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    categories = BreakdownCategory.objects.filter(is_active=True).order_by(
        "order", "code"
    )
    category_codes = (
        [cat.code for cat in categories]
        if categories.exists()
        else ["OO1", "OO2", "OO3", "4.1A", "4.1B", "4.2"]
    )

    data = {
        month_num: {code: 0.0 for code in category_codes} for month_num in range(1, 13)
    }

    for code in category_codes:
        for month_num in range(1, 13):
            metric_field = "payments" if report_type == "disbursement" else "downloads"
            monthly_amount = MasterFundMonitoring.objects.filter(
                mooe=code, date__month=month_num, date__year=current_year
            ).aggregate(total=Sum(metric_field))["total"] or Decimal(0)
            data[month_num][code] = float(monthly_amount)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="mooe_{report_type}_{current_year}.csv"'
    )
    writer = csv.writer(response)
    report_title = "Disbursement" if report_type == "disbursement" else "Downloads"

    writer.writerow([f"MOOE {report_title} Report - Fiscal Year {current_year}"])
    writer.writerow(["Month"] + category_codes + ["Total"])

    for month_num in range(1, 13):
        row = [month_names[month_num - 1]]
        month_total = 0
        for code in category_codes:
            amount = data[month_num][code]
            row.append(round(amount, 2))
            month_total += amount
        row.append(round(month_total, 2))
        writer.writerow(row)

    writer.writerow([])
    writer.writerow(["Quarterly Summary"])
    quarters = [
        ("Q1", [1, 2, 3]),
        ("Q2", [4, 5, 6]),
        ("Q3", [7, 8, 9]),
        ("Q4", [10, 11, 12]),
    ]

    for q_label, q_months in quarters:
        row = [q_label]
        q_total = 0
        for code in category_codes:
            code_total = sum(data[m][code] for m in q_months)
            row.append(round(code_total, 2))
            q_total += code_total
        row.append(round(q_total, 2))
        writer.writerow(row)

    return response


def download_fund(request, report_type):
    """Download fund report (disbursement or downloads) as CSV."""
    from data_management_app.models import FundSource

    current_year = now().year
    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    fund_sources = FundSource.objects.all().order_by("name")
    data = {
        month_num: {fund.id: 0.0 for fund in fund_sources} for month_num in range(1, 13)
    }

    for fund in fund_sources:
        for month_num in range(1, 13):
            metric_field = "payments" if report_type == "disbursement" else "downloads"
            monthly_amount = MasterFundMonitoring.objects.filter(
                fund_source=fund, date__month=month_num, date__year=current_year
            ).aggregate(total=Sum(metric_field))["total"] or Decimal(0)
            data[month_num][fund.id] = float(monthly_amount)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="fund_{report_type}_{current_year}.csv"'
    )
    writer = csv.writer(response)
    report_title = "Disbursement" if report_type == "disbursement" else "Downloads"

    writer.writerow([f"Fund Report {report_title} - Fiscal Year {current_year}"])
    writer.writerow([])
    writer.writerow(["Month"] + [fund.name for fund in fund_sources] + ["Total"])

    for month_num in range(1, 13):
        row = [month_names[month_num - 1]]
        month_total = 0
        for fund in fund_sources:
            amount = data[month_num][fund.id]
            row.append(round(amount, 2))
            month_total += amount
        row.append(round(month_total, 2))
        writer.writerow(row)

    writer.writerow([])
    writer.writerow(["Quarterly Summary"])
    quarters = [
        ("Q1", [1, 2, 3]),
        ("Q2", [4, 5, 6]),
        ("Q3", [7, 8, 9]),
        ("Q4", [10, 11, 12]),
    ]

    for q_label, q_months in quarters:
        row = [q_label]
        q_total = 0
        for fund in fund_sources:
            fund_total = sum(data[m][fund.id] for m in q_months)
            row.append(round(fund_total, 2))
            q_total += fund_total
        row.append(round(q_total, 2))
        writer.writerow(row)

    return response


__all__ = [
    "download_mooe",
    "download_fund",
]
