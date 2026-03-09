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
    from dashboard_app.models import BreakdownCategory, FundSourceBreakdown, MasterFundMonitoring
    
    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]
    
    # Get all breakdown categories
    categories = BreakdownCategory.objects.filter(is_active=True).order_by('order', 'code')
    category_codes = ['OO1', 'OO2', 'OO3', '4.1A', '4.1B', '4.2']
    
    # Calculate budget data for each category
    budget_data = {}
    grand_total_budget = Decimal(0)
    grand_total_disbursed = Decimal(0)
    
    for cat in categories:
        # Annual budget: sum of all fund source breakdowns for this category
        annual_budget = FundSourceBreakdown.objects.filter(
            category=cat
        ).aggregate(total=Sum('budget_amount'))['total'] or Decimal(0)
        
        # Total disbursement: sum of payments where mooe matches this category
        total_disbursed = MasterFundMonitoring.objects.filter(
            mooe=cat.code
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        # Current balance
        current_balance = annual_budget - total_disbursed
        
        # BUR percentage
        if annual_budget > 0:
            bur = (total_disbursed / annual_budget) * 100
        else:
            bur = Decimal(0)
        
        budget_data[cat.code] = {
            'name': cat.name,
            'annual_budget': float(annual_budget),
            'total_disbursed': float(total_disbursed),
            'current_balance': float(current_balance),
            'bur': float(bur),
        }
        
        grand_total_budget += annual_budget
        grand_total_disbursed += total_disbursed
    
    # Calculate grand totals
    grand_balance = grand_total_budget - grand_total_disbursed
    if grand_total_budget > 0:
        grand_bur = (grand_total_disbursed / grand_total_budget) * 100
    else:
        grand_bur = Decimal(0)
    
    # Calculate monthly disbursement and downloads data
    current_year = now().year
    disbursement_data = {}
    downloads_data = {}
    
    # Initialize data structure for months 1-12 and quarters
    for month_num in range(1, 13):
        disbursement_data[month_num] = {}
        downloads_data[month_num] = {}
        for code in category_codes:
            disbursement_data[month_num][code] = 0.0
            downloads_data[month_num][code] = 0.0
    
    # Populate monthly disbursement data
    for code in category_codes:
        for month_num in range(1, 13):
            # Get all transactions for this month and category
            monthly_payments = MasterFundMonitoring.objects.filter(
                mooe=code,
                date__month=month_num,
                date__year=current_year
            ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
            disbursement_data[month_num][code] = float(monthly_payments)
            
            monthly_downloads = MasterFundMonitoring.objects.filter(
                mooe=code,
                date__month=month_num,
                date__year=current_year
            ).aggregate(total=Sum('downloads'))['total'] or Decimal(0)
            downloads_data[month_num][code] = float(monthly_downloads)
    
    # Create breakdown for template: list with month name and data
    disbursement_breakdown = []
    downloads_breakdown = []
    
    # Helper function to calculate row total
    def calc_row_total(data_dict, codes):
        return sum(data_dict.get(code, 0) for code in codes)
    
    # Months 1-3 (Jan, Feb, Mar) + Q1
    row1 = {'name': 'Jan', 'month': 1, 'data': disbursement_data[1], 'total': calc_row_total(disbursement_data[1], category_codes)}
    disbursement_breakdown.append(row1)
    row2 = {'name': 'Feb', 'month': 2, 'data': disbursement_data[2], 'total': calc_row_total(disbursement_data[2], category_codes)}
    disbursement_breakdown.append(row2)
    row3 = {'name': 'Mar', 'month': 3, 'data': disbursement_data[3], 'total': calc_row_total(disbursement_data[3], category_codes)}
    disbursement_breakdown.append(row3)
    
    q1_data = {}
    for code in category_codes:
        q1_data[code] = disbursement_data[1][code] + disbursement_data[2][code] + disbursement_data[3][code]
    q1_row = {'name': '1st Qtr', 'quarter': 1, 'data': q1_data, 'total': calc_row_total(q1_data, category_codes)}
    disbursement_breakdown.append(q1_row)
    
    # Months 4-6
    row4 = {'name': 'Apr', 'month': 4, 'data': disbursement_data[4], 'total': calc_row_total(disbursement_data[4], category_codes)}
    disbursement_breakdown.append(row4)
    row5 = {'name': 'May', 'month': 5, 'data': disbursement_data[5], 'total': calc_row_total(disbursement_data[5], category_codes)}
    disbursement_breakdown.append(row5)
    row6 = {'name': 'Jun', 'month': 6, 'data': disbursement_data[6], 'total': calc_row_total(disbursement_data[6], category_codes)}
    disbursement_breakdown.append(row6)
    
    q2_data = {}
    for code in category_codes:
        q2_data[code] = disbursement_data[4][code] + disbursement_data[5][code] + disbursement_data[6][code]
    q2_row = {'name': '2nd Qtr', 'quarter': 2, 'data': q2_data, 'total': calc_row_total(q2_data, category_codes)}
    disbursement_breakdown.append(q2_row)
    
    # Months 7-9
    row7 = {'name': 'Jul', 'month': 7, 'data': disbursement_data[7], 'total': calc_row_total(disbursement_data[7], category_codes)}
    disbursement_breakdown.append(row7)
    row8 = {'name': 'Aug', 'month': 8, 'data': disbursement_data[8], 'total': calc_row_total(disbursement_data[8], category_codes)}
    disbursement_breakdown.append(row8)
    row9 = {'name': 'Sep', 'month': 9, 'data': disbursement_data[9], 'total': calc_row_total(disbursement_data[9], category_codes)}
    disbursement_breakdown.append(row9)
    
    q3_data = {}
    for code in category_codes:
        q3_data[code] = disbursement_data[7][code] + disbursement_data[8][code] + disbursement_data[9][code]
    q3_row = {'name': '3rd Qtr', 'quarter': 3, 'data': q3_data, 'total': calc_row_total(q3_data, category_codes)}
    disbursement_breakdown.append(q3_row)
    
    # Months 10-12
    row10 = {'name': 'Oct', 'month': 10, 'data': disbursement_data[10], 'total': calc_row_total(disbursement_data[10], category_codes)}
    disbursement_breakdown.append(row10)
    row11 = {'name': 'Nov', 'month': 11, 'data': disbursement_data[11], 'total': calc_row_total(disbursement_data[11], category_codes)}
    disbursement_breakdown.append(row11)
    row12 = {'name': 'Dec', 'month': 12, 'data': disbursement_data[12], 'total': calc_row_total(disbursement_data[12], category_codes)}
    disbursement_breakdown.append(row12)
    
    q4_data = {}
    for code in category_codes:
        q4_data[code] = disbursement_data[10][code] + disbursement_data[11][code] + disbursement_data[12][code]
    q4_row = {'name': '4th Qtr', 'quarter': 4, 'data': q4_data, 'total': calc_row_total(q4_data, category_codes)}
    disbursement_breakdown.append(q4_row)
    
    # Same for downloads
    drow1 = {'name': 'Jan', 'month': 1, 'data': downloads_data[1], 'total': calc_row_total(downloads_data[1], category_codes)}
    downloads_breakdown.append(drow1)
    drow2 = {'name': 'Feb', 'month': 2, 'data': downloads_data[2], 'total': calc_row_total(downloads_data[2], category_codes)}
    downloads_breakdown.append(drow2)
    drow3 = {'name': 'Mar', 'month': 3, 'data': downloads_data[3], 'total': calc_row_total(downloads_data[3], category_codes)}
    downloads_breakdown.append(drow3)
    
    q1_down = {}
    for code in category_codes:
        q1_down[code] = downloads_data[1][code] + downloads_data[2][code] + downloads_data[3][code]
    q1_down_row = {'name': '1st Qtr', 'quarter': 1, 'data': q1_down, 'total': calc_row_total(q1_down, category_codes)}
    downloads_breakdown.append(q1_down_row)
    
    drow4 = {'name': 'Apr', 'month': 4, 'data': downloads_data[4], 'total': calc_row_total(downloads_data[4], category_codes)}
    downloads_breakdown.append(drow4)
    drow5 = {'name': 'May', 'month': 5, 'data': downloads_data[5], 'total': calc_row_total(downloads_data[5], category_codes)}
    downloads_breakdown.append(drow5)
    drow6 = {'name': 'Jun', 'month': 6, 'data': downloads_data[6], 'total': calc_row_total(downloads_data[6], category_codes)}
    downloads_breakdown.append(drow6)
    
    q2_down = {}
    for code in category_codes:
        q2_down[code] = downloads_data[4][code] + downloads_data[5][code] + downloads_data[6][code]
    q2_down_row = {'name': '2nd Qtr', 'quarter': 2, 'data': q2_down, 'total': calc_row_total(q2_down, category_codes)}
    downloads_breakdown.append(q2_down_row)
    
    drow7 = {'name': 'Jul', 'month': 7, 'data': downloads_data[7], 'total': calc_row_total(downloads_data[7], category_codes)}
    downloads_breakdown.append(drow7)
    drow8 = {'name': 'Aug', 'month': 8, 'data': downloads_data[8], 'total': calc_row_total(downloads_data[8], category_codes)}
    downloads_breakdown.append(drow8)
    drow9 = {'name': 'Sep', 'month': 9, 'data': downloads_data[9], 'total': calc_row_total(downloads_data[9], category_codes)}
    downloads_breakdown.append(drow9)
    
    q3_down = {}
    for code in category_codes:
        q3_down[code] = downloads_data[7][code] + downloads_data[8][code] + downloads_data[9][code]
    q3_down_row = {'name': '3rd Qtr', 'quarter': 3, 'data': q3_down, 'total': calc_row_total(q3_down, category_codes)}
    downloads_breakdown.append(q3_down_row)
    
    drow10 = {'name': 'Oct', 'month': 10, 'data': downloads_data[10], 'total': calc_row_total(downloads_data[10], category_codes)}
    downloads_breakdown.append(drow10)
    drow11 = {'name': 'Nov', 'month': 11, 'data': downloads_data[11], 'total': calc_row_total(downloads_data[11], category_codes)}
    downloads_breakdown.append(drow11)
    drow12 = {'name': 'Dec', 'month': 12, 'data': downloads_data[12], 'total': calc_row_total(downloads_data[12], category_codes)}
    downloads_breakdown.append(drow12)
    
    q4_down = {}
    for code in category_codes:
        q4_down[code] = downloads_data[10][code] + downloads_data[11][code] + downloads_data[12][code]
    q4_down_row = {'name': '4th Qtr', 'quarter': 4, 'data': q4_down, 'total': calc_row_total(q4_down, category_codes)}
    downloads_breakdown.append(q4_down_row)
    
    context = {
        "months": months,
        "budget_data": budget_data,
        "category_codes": category_codes,
        "grand_total_budget": float(grand_total_budget),
        "grand_total_disbursed": float(grand_total_disbursed),
        "grand_balance": float(grand_balance),
        "grand_bur": float(grand_bur),
        "disbursement_breakdown": disbursement_breakdown,
        "downloads_breakdown": downloads_breakdown,
    }
    
    return render(request, "reports/mooe_report.html", context)


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
    """Generate fund report by fund source"""
    from dashboard_app.models import FundSource, MasterFundMonitoring
    from django.db.models import Sum
    from datetime import datetime
    
    months = [
        "Jan", "Feb", "Mar", "1st Qtr",
        "Apr", "May", "Jun", "2nd Qtr",
        "Jul", "Aug", "Sep", "3rd Qtr",
        "Oct", "Nov", "Dec", "4th Qtr"
    ]
    
    # Get all fund sources
    fund_sources = FundSource.objects.all().order_by('name')
    fund_codes = [fund.id for fund in fund_sources]
    current_year = datetime.now().year
    
    # Build budget data for each fund
    budget_data = {}
    grand_total_budget = 0
    grand_total_disbursed = 0
    grand_total_downloads = 0
    
    for fund in fund_sources:
        # Annual budget
        annual_budget = fund.annual_budget or 0
        
        # Total disbursement
        total_disbursed = MasterFundMonitoring.objects.filter(
            fund_source=fund
        ).aggregate(total=Sum('payments'))['total'] or 0
        
        # Total downloads
        total_downloads = MasterFundMonitoring.objects.filter(
            fund_source=fund
        ).aggregate(total=Sum('downloads'))['total'] or 0
        
        # Calculate balance and BUR%
        current_balance = float(annual_budget) - float(total_disbursed)
        bur_percent = (float(total_disbursed) / float(annual_budget) * 100) if annual_budget > 0 else 0
        
        budget_data[fund.id] = {
            'annual_budget': float(annual_budget),
            'total_disbursed': float(total_disbursed),
            'total_downloads': float(total_downloads),
            'current_balance': current_balance,
            'bur_percent': bur_percent,
        }
        
        grand_total_budget += float(annual_budget)
        grand_total_disbursed += float(total_disbursed)
        grand_total_downloads += float(total_downloads)
    
    grand_total_balance = grand_total_budget - grand_total_disbursed
    grand_total_bur = (grand_total_disbursed / grand_total_budget * 100) if grand_total_budget > 0 else 0
    
    # Build monthly breakdown data
    disbursement_data = {}
    downloads_data = {}
    
    for month_num in range(1, 13):
        disbursement_data[month_num] = {}
        downloads_data[month_num] = {}
        
        for fund in fund_sources:
            month_disbursement = MasterFundMonitoring.objects.filter(
                fund_source=fund,
                date__month=month_num,
                date__year=current_year
            ).aggregate(total=Sum('payments'))['total'] or 0
            
            month_downloads = MasterFundMonitoring.objects.filter(
                fund_source=fund,
                date__month=month_num,
                date__year=current_year
            ).aggregate(total=Sum('downloads'))['total'] or 0
            
            disbursement_data[month_num][fund.id] = float(month_disbursement)
            downloads_data[month_num][fund.id] = float(month_downloads)
    
    # Build monthly breakdown lists with quarterly totals
    def calc_row_total(data_dict, codes):
        return sum(data_dict.get(code, 0) for code in codes)
    
    disbursement_breakdown = []
    downloads_breakdown = []
    
    # Build quarterly data first
    q_data = [{}, {}, {}, {}]  # q_data[0] = Q1, etc.
    q_dl = [{}, {}, {}, {}]
    
    for fund in fund_sources:
        q_data[0][fund.id] = disbursement_data[1][fund.id] + disbursement_data[2][fund.id] + disbursement_data[3][fund.id]
        q_data[1][fund.id] = disbursement_data[4][fund.id] + disbursement_data[5][fund.id] + disbursement_data[6][fund.id]
        q_data[2][fund.id] = disbursement_data[7][fund.id] + disbursement_data[8][fund.id] + disbursement_data[9][fund.id]
        q_data[3][fund.id] = disbursement_data[10][fund.id] + disbursement_data[11][fund.id] + disbursement_data[12][fund.id]
        
        q_dl[0][fund.id] = downloads_data[1][fund.id] + downloads_data[2][fund.id] + downloads_data[3][fund.id]
        q_dl[1][fund.id] = downloads_data[4][fund.id] + downloads_data[5][fund.id] + downloads_data[6][fund.id]
        q_dl[2][fund.id] = downloads_data[7][fund.id] + downloads_data[8][fund.id] + downloads_data[9][fund.id]
        q_dl[3][fund.id] = downloads_data[10][fund.id] + downloads_data[11][fund.id] + downloads_data[12][fund.id]
    
    # Add months and quarters in interleaved order:
    # Jan, Feb, Mar, 1st Qtr, Apr, May, Jun, 2nd Qtr, etc.
    months_per_qtr = [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (10, 11, 12),
    ]
    quarter_names = ['1st Qtr', '2nd Qtr', '3rd Qtr', '4th Qtr']
    
    for qtr_idx, (m1, m2, m3) in enumerate(months_per_qtr):
        # Add 3 months for this quarter
        for month_num in [m1, m2, m3]:
            row_total = calc_row_total(disbursement_data[month_num], fund_codes)
            disbursement_breakdown.append({
                'month': months[month_num - 1],
                'month_num': month_num,
                'data': disbursement_data[month_num],
                'total': row_total,
                'quarter': None,
            })
            
            row_total = calc_row_total(downloads_data[month_num], fund_codes)
            downloads_breakdown.append({
                'month': months[month_num - 1],
                'month_num': month_num,
                'data': downloads_data[month_num],
                'total': row_total,
                'quarter': None,
            })
        
        # Add quarterly total after 3 months
        disbursement_breakdown.append({
            'month': quarter_names[qtr_idx],
            'month_num': 0,
            'quarter': qtr_idx + 1,
            'data': q_data[qtr_idx],
            'total': calc_row_total(q_data[qtr_idx], fund_codes),
        })
        
        downloads_breakdown.append({
            'month': quarter_names[qtr_idx],
            'month_num': 0,
            'quarter': qtr_idx + 1,
            'data': q_dl[qtr_idx],
            'total': calc_row_total(q_dl[qtr_idx], fund_codes),
        })
    
    return render(request, "reports/fund_report.html", {
        "months": months,
        "fund_sources": fund_sources,
        "fund_codes": fund_codes,
        "budget_data": budget_data,
        "disbursement_breakdown": disbursement_breakdown,
        "downloads_breakdown": downloads_breakdown,
        "grand_total_budget": grand_total_budget,
        "grand_total_disbursed": grand_total_disbursed,
        "grand_total_downloads": grand_total_downloads,
        "grand_total_balance": grand_total_balance,
        "grand_total_bur": grand_total_bur,
    })


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
