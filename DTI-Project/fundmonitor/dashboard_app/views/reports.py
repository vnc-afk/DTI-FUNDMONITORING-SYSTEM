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
    
    # Month names only (no quarters)
    month_names = [
        "Jan", "Feb", "Mar",
        "Apr", "May", "Jun",
        "Jul", "Aug", "Sep",
        "Oct", "Nov", "Dec"
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
    
    # Add individual month rows only (no quarterly totals - JS calculates them)
    for month_num in range(1, 13):
        row_total = calc_row_total(disbursement_data[month_num], category_codes)
        disbursement_breakdown.append({
            'month': month_names[month_num - 1],
            'month_num': month_num,
            'data': disbursement_data[month_num],
            'total': row_total,
            'quarter': None,
        })
        
        row_total = calc_row_total(downloads_data[month_num], category_codes)
        downloads_breakdown.append({
            'month': month_names[month_num - 1],
            'month_num': month_num,
            'data': downloads_data[month_num],
            'total': row_total,
            'quarter': None,
        })
    
    # Prepare data for JavaScript rendering
    mooe_report_data = {
        'categoryCodes': category_codes,
        'budgetData': budget_data,
        'disbursementBreakdown': disbursement_breakdown,
        'downloadsBreakdown': downloads_breakdown,
        'grandTotalBudget': float(grand_total_budget),
        'grandTotalDisbursed': float(grand_total_disbursed),
        'grandBalance': float(grand_balance),
        'grandBur': float(grand_bur),
    }
    
    context = {
        "mooe_report_json": json.dumps(mooe_report_data),
        "grand_total_budget": float(grand_total_budget),
        "grand_total_disbursed": float(grand_total_disbursed),
        "grand_balance": float(grand_balance),
        "grand_bur": float(grand_bur),
    }
    
    return render(request, "reports/mooe_report.html", context)


def nc_report(request):
    """Generate Negosyo Center report by district and municipality"""
    from dashboard_app.models import NegosyoCenter, District, FundSource
    from datetime import datetime
    from collections import defaultdict
    
    current_year = datetime.now().year
    
    # Get all districts with their Negosyo Centers
    districts = District.objects.prefetch_related('negosyo_centers').order_by('order', 'name')
    
    # Month names for display
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Prepare district data
    districts_data = []
    total_disbursement = 0.0
    total_downloads = 0.0
    
    for district in districts:
        negosyo_centers = district.negosyo_centers.filter(is_active=True).order_by('name')
        
        if not negosyo_centers.exists():
            continue
        
        # Get all transactions for this district's NC locations
        nc_ids = negosyo_centers.values_list('id', flat=True)
        transactions = MasterFundMonitoring.objects.filter(
            nc_id__in=nc_ids,
            date__year=current_year
        ).order_by('nc__name', 'date')
        
        # Initialize monthly data structure
        # monthly_data[month_num][nc_id] = amount
        monthly_data = {m: {} for m in range(1, 13)}
        
        # Initialize NC totals per month
        for nc in negosyo_centers:
            for month_num in range(1, 13):
                monthly_data[month_num][nc.id] = 0.0
        
        # Aggregate transaction data by month and NC
        for transaction in transactions:
            month_num = transaction.date.month
            nc_id = transaction.nc_id
            payment = float(transaction.payments or 0)
            monthly_data[month_num][nc_id] += payment
            total_disbursement += payment
            total_downloads += float(transaction.downloads or 0)
        
        # Create quarterly breakdown structure
        quarters = []
        quarter_configs = [
            {'months': [1, 2, 3], 'label': 'Q1', 'range': 'January – March'},
            {'months': [4, 5, 6], 'label': 'Q2', 'range': 'April – June'},
            {'months': [7, 8, 9], 'label': 'Q3', 'range': 'July – September'},
            {'months': [10, 11, 12], 'label': 'Q4', 'range': 'October – December'},
        ]
        
        # Build quarterly data
        for qtr_config in quarter_configs:
            qtr_months = []
            qtr_total = 0
            
            for month_num in qtr_config['months']:
                month_row = {
                    'name': month_names[month_num - 1],
                    'month_num': month_num,
                    'nc_data': {},  # nc_id -> amount
                    'month_total': 0,
                }
                
                for nc in negosyo_centers:
                    amount = monthly_data[month_num].get(nc.id, 0.0)
                    month_row['nc_data'][nc.id] = amount
                    month_row['month_total'] += amount
                    qtr_total += amount
                
                qtr_months.append(month_row)
            
            quarter = {
                'label': qtr_config['label'],
                'range': qtr_config['range'],
                'months': qtr_months,
                'total': qtr_total,
            }
            quarters.append(quarter)
        
        district_data = {
            'name': district.name,
            'order': district.order,
            'negosyo_centers': [
                {'id': nc.id, 'name': nc.name}
                for nc in negosyo_centers
            ],
            'quarters': quarters,
            'district_total': sum(q['total'] for q in quarters),
        }
        
        districts_data.append(district_data)
    
    # Calculate budget totals
    annual_budget = FundSource.objects.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    annual_budget = float(annual_budget)
    
    # Calculate balance and BUR
    current_balance = annual_budget - total_disbursement
    bur_rate = (total_disbursement / annual_budget * 100) if annual_budget > 0 else 0
    
    # Prepare data for JavaScript rendering
    nc_report_data = {
        'districts': districts_data,
        'totalDisbursement': total_disbursement,
        'totalDownloads': total_downloads,
        'annualBudget': annual_budget,
        'currentBalance': current_balance,
        'burRate': bur_rate,
    }
    
    context = {
        'nc_report_json': json.dumps(nc_report_data),
        'annual_budget': annual_budget,
        'total_disbursement': total_disbursement,
        'total_downloads': total_downloads,
        'current_balance': current_balance,
        'bur_rate': bur_rate,
    }
    
    return render(request, "reports/negosyo_center_report.html", context)


def fund_report(request):
    """Generate fund report by fund source"""
    from dashboard_app.models import FundSource, MasterFundMonitoring
    from django.db.models import Sum
    from datetime import datetime
    
    # Month names only (no quarters)
    month_names = [
        "Jan", "Feb", "Mar",
        "Apr", "May", "Jun",
        "Jul", "Aug", "Sep",
        "Oct", "Nov", "Dec"
    ]
    
    # Get only active fund sources (budget > 0)
    fund_sources = FundSource.objects.filter(annual_budget__gt=0).order_by('name')
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
    
    # Add individual month rows only (no quarterly totals - JS calculates them)
    for month_num in range(1, 13):
        row_total = calc_row_total(disbursement_data[month_num], fund_codes)
        disbursement_breakdown.append({
            'month': month_names[month_num - 1],
            'month_num': month_num,
            'data': disbursement_data[month_num],
            'total': row_total,
            'quarter': None,
        })
        
        row_total = calc_row_total(downloads_data[month_num], fund_codes)
        downloads_breakdown.append({
            'month': month_names[month_num - 1],
            'month_num': month_num,
            'data': downloads_data[month_num],
            'total': row_total,
            'quarter': None,
        })
    
    # Prepare data for JavaScript rendering
    fund_report_data = {
        'funds': [{'id': f.id, 'name': f.name} for f in fund_sources],
        'budgetData': budget_data,
        'disbursementBreakdown': disbursement_breakdown,
        'downloadsBreakdown': downloads_breakdown,
        'grandTotalBudget': grand_total_budget,
        'grandTotalDisbursed': grand_total_disbursed,
        'grandTotalDownloads': grand_total_downloads,
        'grandTotalBalance': grand_total_balance,
        'grandTotalBur': grand_total_bur,
    }
    
    return render(request, "reports/fund_report.html", {
        "fund_report_json": json.dumps(fund_report_data),
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
