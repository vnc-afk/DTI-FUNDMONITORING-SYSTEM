from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils.timezone import now
from dashboard_app.models import ExpenseObject, MasterFundMonitoring
import csv
import json
from decimal import Decimal


def expense_report(request):
    """Generate expense report with monthly breakdown"""
    # Fetch all active expense objects
    object = ExpenseObject.objects.filter(is_active=True).values('id', 'code', 'name', 'color')
    
    # Prepare objects for template with monthly data
    current_year = now().year
    expense_data = []
    
    for cat in object:
        # Query expenses for this category from MasterFundMonitoring
        expenses = MasterFundMonitoring.objects.filter(
            account_title_id=cat['id'],
            date__year=current_year
        ).values_list('date', 'payments')
        
        # Initialize quarterly arrays
        q1 = [Decimal(0), Decimal(0), Decimal(0)]  # Jan, Feb, Mar
        q2 = [Decimal(0), Decimal(0), Decimal(0)]  # Apr, May, Jun
        q3 = [Decimal(0), Decimal(0), Decimal(0)]  # Jul, Aug, Sep
        q4 = [Decimal(0), Decimal(0), Decimal(0)]  # Oct, Nov, Dec
        
        # Populate with actual data
        for date, payment in expenses:
            if date and payment:
                month = date.month - 1  # 0-indexed
                quarter_idx = month // 3
                month_in_quarter = month % 3
                
                if quarter_idx == 0:
                    q1[month_in_quarter] += Decimal(str(payment))
                elif quarter_idx == 1:
                    q2[month_in_quarter] += Decimal(str(payment))
                elif quarter_idx == 2:
                    q3[month_in_quarter] += Decimal(str(payment))
                elif quarter_idx == 3:
                    q4[month_in_quarter] += Decimal(str(payment))
        
        # Convert to floats for JSON serialization
        expense_data.append({
            'name': f"({cat['code']}) {cat['name']}",
            'color': cat['color'],
            'q1': [float(x) for x in q1],
            'q2': [float(x) for x in q2],
            'q3': [float(x) for x in q3],
            'q4': [float(x) for x in q4]
        })
    
    # Convert to JSON for JavaScript
    expense_json = json.dumps(expense_data)
    
    return render(request, 'reports/expenses_report.html', {
        'report_data': expense_data,
        'expense_json': expense_json
    })


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
