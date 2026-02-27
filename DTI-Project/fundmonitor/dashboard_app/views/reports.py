from django.shortcuts import render
from django.http import HttpResponse
import csv


def expense_report(request):
    """Generate expense report with monthly breakdown"""
    # placeholder dataset for demonstration; replace with real query logic later
    report_data = []
    return render(request, 'reports/expenses_report.html', {'report_data': report_data})


def mooe_report(request):
    """Generate MOOE (Maintenance and Other Operating Expenses) report"""
    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]
    return render(request, "reports/mooe_report.html", {"months": months})


def nc_report(request):
    """Generate Negosyo Center report"""
    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]
    return render(request, "reports/negosyo_center_report.html", {"months": months})


def fund_report(request):
    """Generate fund report"""
    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]
    return render(request, "reports/fund_report.html", {"months": months})


def download_mooe(request, report_type):
    """Download MOOE report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Month', 'OO1', 'OO2', 'OO3', '4.1A', '4.1B', '4.2', 'Total'])

    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]

    for m in months:
        writer.writerow([m, 0, 0, 0, 0, 0, 0, 0])

    return response


def tin(request):
    """Display TIN (Taxpayer Identification Number) report"""
    return render(request, 'reports/allocations/tin.html')
