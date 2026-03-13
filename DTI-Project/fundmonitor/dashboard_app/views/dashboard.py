from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils.timezone import now
from django.http import JsonResponse
import json
from decimal import Decimal
from dashboard_app.models import (
    MasterFundMonitoring, FundSource, Supplier, 
    ExpenseObject, ExpenseCategory, Staff, Division,
    District, NegosyoCenter, BankStatement, BankAccount
)


def get_filter_parameters(request):
    """Extract and validate filter parameters from request"""
    filters = {}
    
    # Year filter
    year = request.GET.get('year')
    filters['year'] = int(year) if year and year.isdigit() else now().year
    
    # Fund Source filter
    if request.GET.get('fund_source'):
        filters['fund_source_id'] = request.GET.get('fund_source')
    
    # Division filter
    if request.GET.get('division'):
        filters['division_id'] = request.GET.get('division')
    
    # District filter
    if request.GET.get('district'):
        filters['nc__district_id'] = request.GET.get('district')
    
    # Expense Classification filter
    if request.GET.get('expense_class'):
        filters['expense_classification_id'] = request.GET.get('expense_class')
    
    # Supplier filter
    if request.GET.get('supplier'):
        filters['payee_id'] = request.GET.get('supplier')
    
    # Staff filter
    if request.GET.get('staff'):
        filters['division__staff'] = request.GET.get('staff')
    
    return filters


def dashboard(request):
    """
    Main dashboard view with comprehensive analytics and filtering.
    """
    current_year = now().year
    
    # Get available years from both transaction and bank statement data
    transaction_years = set(
        MasterFundMonitoring.objects.values_list('date__year', flat=True).distinct()
    )
    bank_years = set(
        BankStatement.objects.all().values_list('date__year', flat=True)
    )
    
    # Combine all years and use the latest as default
    all_available_years = transaction_years | bank_years
    default_year = max(all_available_years) if all_available_years else current_year
    
    year_filter = int(request.GET.get('year')) if request.GET.get('year') else default_year
    
    # Build filter dictionary
    filters = {}
    if request.GET.get('year'):
        filters['date__year'] = int(request.GET.get('year'))
    else:
        filters['date__year'] = default_year
    
    if request.GET.get('fund_source'):
        filters['fund_source_id'] = request.GET.get('fund_source')
    
    if request.GET.get('division'):
        filters['division_id'] = request.GET.get('division')
    
    if request.GET.get('district'):
        filters['nc__district_id'] = request.GET.get('district')
    
    if request.GET.get('expense_class'):
        filters['expense_classification_id'] = request.GET.get('expense_class')
    
    if request.GET.get('supplier'):
        filters['payee_id'] = request.GET.get('supplier')
    
    # Base queryset with filters
    transaction_qs = MasterFundMonitoring.objects.filter(**filters)
    
    # ====== 1. KPI SUMMARY CARDS ======
    total_budget = FundSource.objects.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    
    # Calculate active funds (those with budget > 0)
    all_fund_sources = FundSource.objects.all()
    active_funds = all_fund_sources.filter(annual_budget__gt=0)
    active_fund_count = active_funds.count()
    active_total_budget = active_funds.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    
    # Calculate disbursements (excluding refunds and adjustments)
    disbursement_qs = transaction_qs.filter(transaction_type='Disbursement')
    total_disbursement = disbursement_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate downloads (which reduce available budget)
    downloads_qs = transaction_qs.filter(transaction_type='Downloads')
    total_downloads_trans = downloads_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate refunds (which reduce the disbursement)
    refund_qs = transaction_qs.filter(transaction_type='Refund')
    total_refunds = refund_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate adjustments (treated as disbursements for now)
    adjustment_qs = transaction_qs.filter(transaction_type='Adjustment')
    total_adjustments = adjustment_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Remaining balance = Total Budget - Disbursements - Downloads - Adjustments + Refunds
    remaining_balance = total_budget - total_disbursement - total_downloads_trans - total_adjustments + total_refunds
    
    # Budget utilization rate is based on net disbursement (disbursements + downloads + adjustments - refunds)
    net_disbursement = total_disbursement + total_downloads_trans + total_adjustments - total_refunds
    budget_utilization_rate = (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    total_transactions = transaction_qs.count()
    total_suppliers_paid = transaction_qs.values('payee').distinct().count()
    
    # ====== 2. MONTHLY DISBURSEMENT TREND ======
    monthly_data = {}
    monthly_downloads = {}
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month in range(1, 13):
        # Sum disbursements, downloads, and adjustments (exclude refunds from trend)
        month_sum = transaction_qs.filter(
            date__month=month,
            transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        monthly_data[month_names[month - 1]] = float(month_sum)
        
        # Sum downloads for monthly trend
        month_downloads = transaction_qs.filter(
            date__month=month
        ).aggregate(total=Sum('downloads'))['total'] or Decimal(0)
        monthly_downloads[month_names[month - 1]] = float(month_downloads)
    
    # ====== 3. REMAINING AVAILABLE BY FUND SOURCE (DONUT) ======
    fund_remaining = []
    for fs in FundSource.objects.all():
        # Calculate disbursements and downloads transaction type (excluding refunds)
        disbursed = transaction_qs.filter(
            fund_source=fs,
            transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        # Calculate refunds (which reduce net disbursed)
        refunded = transaction_qs.filter(
            fund_source=fs,
            transaction_type='Refund'
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        # Calculate total downloads field amount (MDP - additional allocation from higher office)
        downloads_amt = transaction_qs.filter(
            fund_source=fs
        ).aggregate(total=Sum('downloads'))['total'] or Decimal(0)
        
        # Net disbursed = disbursements + downloads transaction type - refunds
        net_disbursed = disbursed - refunded
        # Remaining = Annual budget + Downloads field (MDP) - Net disbursed
        remaining = fs.annual_budget + downloads_amt - net_disbursed
        if remaining > 0:  # Only include fund sources with remaining balance
            fund_remaining.append({
                'name': fs.name,
                'remaining': float(remaining)
            })
    
    # Sort by remaining amount (descending)
    fund_remaining.sort(key=lambda x: x['remaining'], reverse=True)
    
    fund_labels = [item['name'] for item in fund_remaining]
    fund_values = [item['remaining'] for item in fund_remaining]
    
    # ====== 4. BUDGET VS DISBURSEMENT (BAR CHART) ======
    budget_vs_disburse = []
    for fs in FundSource.objects.all():
        # Calculate net disbursed = disbursements + adjustments - refunds
        disburse = transaction_qs.filter(
            fund_source=fs,
            transaction_type__in=['Disbursement', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        refund = transaction_qs.filter(
            fund_source=fs,
            transaction_type='Refund'
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        net_disbursed = disburse - refund
        
        budget_vs_disburse.append({
            'name': fs.name,
            'budget': float(fs.annual_budget),
            'disbursed': float(net_disbursed)
        })
    
    budget_labels = [item['name'] for item in budget_vs_disburse]
    budget_amounts = [item['budget'] for item in budget_vs_disburse]
    disburse_amounts = [item['disbursed'] for item in budget_vs_disburse]
    
    # ====== 5. ACCOUNT TITLE / EXPENSE OBJECTS ANALYSIS (HORIZONTAL BAR) ======
    expense_analysis = transaction_qs.filter(
        account_title__isnull=False
    ).values(
        'account_title__name'
    ).annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    expense_labels = [item['account_title__name'] for item in expense_analysis]
    expense_values = [float(item['total'] or 0) for item in expense_analysis]
    
    # ====== 6. TOP SUPPLIERS / PAYEES (BAR CHART - TOP 10) ======
    top_suppliers = transaction_qs.filter(
        payee__supplier__isnull=False
    ).values('payee__supplier').annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    supplier_labels = [item['payee__supplier'] for item in top_suppliers]
    supplier_values = [float(item['total'] or 0) for item in top_suppliers]
    
    # ====== 7. MOOE BREAKDOWN REMAINING BALANCE (DONUT) ======
    # Get ALL breakdown categories, not just those with transactions
    mooe_remaining = []
    try:
        from dashboard_app.models import BreakdownCategory, FundSourceBreakdown
        all_categories = BreakdownCategory.objects.filter(is_active=True).order_by('order')
        
        for category in all_categories:
            mooe_code = category.code
            
            # Calculate remaining = budget + downloads - disbursed
            mooe_disbursed = transaction_qs.filter(
                mooe=mooe_code,
                transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
            ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
            
            mooe_refunded = transaction_qs.filter(
                mooe=mooe_code,
                transaction_type='Refund'
            ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
            
            mooe_downloads = transaction_qs.filter(
                mooe=mooe_code
            ).aggregate(total=Sum('downloads'))['total'] or Decimal(0)
            
            # Get budget for this MOOE category (sum of all fund source breakdowns)
            mooe_budget = FundSourceBreakdown.objects.filter(
                category__code=mooe_code
            ).aggregate(total=Sum('budget_amount'))['total'] or Decimal(0)
            
            # Net disbursed = disbursements + downloads transaction type - refunds
            net_mooe_disbursed = mooe_disbursed - mooe_refunded
            # Remaining = Budget + Downloads field (MDP) - Net disbursed
            remaining = mooe_budget + mooe_downloads - net_mooe_disbursed
            
            # Always include all categories so we can see which ones are fully allocated
            mooe_remaining.append({
                'name': category.name or mooe_code,
                'remaining': float(remaining)
            })
    except Exception as e:
        print(f'Error loading MOOE categories: {e}')
    
    # Sort by remaining amount (descending)
    mooe_remaining.sort(key=lambda x: x['remaining'], reverse=True)
    
    mooe_labels = [item['name'] for item in mooe_remaining]
    mooe_values = [item['remaining'] for item in mooe_remaining]
    
    # ====== 8. CHEQUE MONITORING (DONUT) ======
    cheque_status = transaction_qs.filter(
        cheque_status__isnull=False
    ).values('cheque_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    cheque_labels = [item['cheque_status'] for item in cheque_status]
    cheque_counts = [item['count'] for item in cheque_status]
    
    # ====== 9. DISTRICT SPENDING (STACKED COLUMN) ======
    district_spending = transaction_qs.filter(
        nc__district__isnull=False
    ).values(
        'nc__district__name'
    ).annotate(
        total=Sum('payments')
    ).order_by('-total')
    
    district_labels = [item['nc__district__name'] for item in district_spending]
    district_values = [float(item['total'] or 0) for item in district_spending]
    
    # ====== 10. BANK BALANCE TREND (AREA CHART) ======
    # Bank statements are independent of transaction filters - show all for the year
    year_to_filter = int(year_filter) if year_filter else default_year
    bank_statements = BankStatement.objects.filter(
        date__year=year_to_filter
    ).order_by('date')
    
    bank_dates = [str(stmt.date) for stmt in bank_statements]
    bank_debits = [float(stmt.debit or 0) for stmt in bank_statements]
    bank_credits = [float(stmt.credit or 0) for stmt in bank_statements]
    bank_balances = [float(stmt.balance or 0) for stmt in bank_statements]
    
    # Debug: Log if no bank statements found
    if not bank_statements:
        print(f"⚠️  No BankStatement records found for year {year_to_filter}")
    
    # ====== FILTER OPTIONS ======
    # Reuse years already calculated at the top (all_available_years)
    years = sorted(all_available_years)
    
    # Only show active fund sources (budget > 0) in dropdowns
    fund_sources = FundSource.objects.filter(annual_budget__gt=0)
    divisions = Division.objects.all()
    districts = District.objects.all()
    expense_classifications = ExpenseCategory.objects.all()
    suppliers = Supplier.objects.all()
    
    context = {
        # KPIs
        'total_budget': float(total_budget),
        'active_fund_count': active_fund_count,
        'active_total_budget': float(active_total_budget),
        'total_disbursement': float(total_disbursement),
        'remaining_balance': float(remaining_balance),
        'budget_utilization_rate': round(budget_utilization_rate, 2),
        'total_transactions': total_transactions,
        'total_suppliers_paid': total_suppliers_paid,
        
        # Chart data (JSON)
        'monthly_data': json.dumps(monthly_data),
        'monthly_downloads': json.dumps(monthly_downloads),
        'fund_labels': json.dumps(fund_labels),
        'fund_values': json.dumps(fund_values),
        'budget_labels': json.dumps(budget_labels),
        'budget_amounts': json.dumps(budget_amounts),
        'disburse_amounts': json.dumps(disburse_amounts),
        'expense_labels': json.dumps(expense_labels),
        'expense_values': json.dumps(expense_values),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'mooe_labels': json.dumps(mooe_labels),
        'mooe_values': json.dumps(mooe_values),
        'cheque_labels': json.dumps(cheque_labels),
        'cheque_counts': json.dumps(cheque_counts),
        'district_labels': json.dumps(district_labels),
        'district_values': json.dumps(district_values),
        'bank_dates': json.dumps(bank_dates),
        'bank_debits': json.dumps(bank_debits),
        'bank_credits': json.dumps(bank_credits),
        'bank_balances': json.dumps(bank_balances),
        
        # Filter options
        'years': years,
        'fund_sources': fund_sources,
        'divisions': divisions,
        'districts': districts,
        'expense_classifications': expense_classifications,
        'suppliers': suppliers,
        'current_year': int(year_filter) if year_filter else default_year,
        
        # Current filter values (for preserving selections)
        'selected_year': request.GET.get('year', str(default_year)),
        'selected_fund_source': request.GET.get('fund_source', ''),
        'selected_division': request.GET.get('division', ''),
        'selected_district': request.GET.get('district', ''),
        'selected_expense_class': request.GET.get('expense_class', ''),
        'selected_date_month': request.GET.get('date_month', ''),
    }
    
    return render(request, 'dashboard.html', context)


def get_dashboard_data(request):
    """
    API endpoint for dashboard data (JSON format).
    """
    current_year = now().year
    filters = {'date__year': current_year}
    
    transaction_qs = MasterFundMonitoring.objects.filter(**filters)
    
    total_budget = FundSource.objects.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    
    # Calculate disbursements (excluding refunds and adjustments)
    disbursement_qs = transaction_qs.filter(transaction_type='Disbursement')
    total_disbursement = disbursement_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate refunds (which reduce the disbursement)
    refund_qs = transaction_qs.filter(transaction_type='Refund')
    total_refunds = refund_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate adjustments (treated as disbursements for now)
    adjustment_qs = transaction_qs.filter(transaction_type='Adjustment')
    total_adjustments = adjustment_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Remaining balance = Total Budget - Disbursements - Adjustments + Refunds
    remaining_balance = total_budget - total_disbursement - total_adjustments + total_refunds
    
    # Budget utilization rate is based on net disbursement
    net_disbursement = total_disbursement + total_adjustments - total_refunds
    budget_utilization_rate = (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    
    data = {
        'total_budget': float(total_budget),
        'total_disbursement': float(total_disbursement),
        'remaining_balance': float(remaining_balance),
        'budget_utilization_rate': round(budget_utilization_rate, 2),
        'year': current_year,
    }
    
    return JsonResponse(data)


def executive_dashboard(request):
    """
    Executive/Provincial Director Dashboard - High-level fund health overview.
    Displays key metrics at a glance.
    """
    current_year = now().year
    
    # Get available years from transaction data
    transaction_years = set(
        MasterFundMonitoring.objects.values_list('date__year', flat=True).distinct()
    )
    default_year = max(transaction_years) if transaction_years else current_year
    year_filter = int(request.GET.get('year')) if request.GET.get('year') else default_year
    
    # Filter transactions by year
    filters = {'date__year': year_filter}
    transaction_qs = MasterFundMonitoring.objects.filter(**filters)
    
    # ====== KEY KPI CALCULATIONS ======
    # Total budget across all funds
    total_budget = FundSource.objects.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    
    # Net disbursements = (Disbursement + Downloads + Adjustment) - Refunds
    disbursement_total = transaction_qs.filter(
        transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
    ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    refund_total = transaction_qs.filter(
        transaction_type='Refund'
    ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    net_disbursement = disbursement_total - refund_total
    remaining_balance = total_budget - net_disbursement
    
    # Budget utilization percentage
    budget_utilization_pct = (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    
    # Determine budget health status
    if budget_utilization_pct > 100:
        budget_status = 'OVER_BUDGET'
        status_label = '⚠️ OVER BUDGET'
        status_color = '#e74c3c'  # Red
    elif budget_utilization_pct >= 80:
        budget_status = 'CRITICAL'
        status_label = '🔴 CRITICAL (80%+)'
        status_color = '#e67e22'  # Orange
    elif budget_utilization_pct >= 60:
        budget_status = 'HIGH'
        status_label = '🟡 HIGH (60%+)'
        status_color = '#f39c12'  # Yellow
    else:
        budget_status = 'HEALTHY'
        status_label = '🟢 HEALTHY'
        status_color = '#27ae60'  # Green
    
    # ====== FUND-BY-FUND BREAKDOWN ======
    funds_data = []
    for fund in FundSource.objects.all().order_by('-annual_budget'):
        if fund.annual_budget == 0:
            continue
            
        fund_disburse = transaction_qs.filter(
            fund_source=fund,
            transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        fund_refund = transaction_qs.filter(
            fund_source=fund,
            transaction_type='Refund'
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        
        fund_net = fund_disburse - fund_refund
        fund_remaining = fund.annual_budget - fund_net
        fund_utilization = (float(fund_net) / float(fund.annual_budget) * 100) if fund.annual_budget > 0 else 0
        
        # Fund status
        if fund_utilization > 100:
            f_status = 'OVER'
            f_color = '#e74c3c'
        elif fund_utilization >= 80:
            f_status = 'CRITICAL'
            f_color = '#e67e22'
        elif fund_utilization >= 60:
            f_status = 'CAUTION'
            f_color = '#f39c12'
        else:
            f_status = 'OK'
            f_color = '#27ae60'
        
        funds_data.append({
            'name': fund.name,
            'budget': float(fund.annual_budget),
            'spent': float(fund_net),
            'remaining': float(fund_remaining),
            'utilization': round(fund_utilization, 1),
            'status': f_status,
            'color': f_color,
        })
    
    # ====== MONTHLY SPENDING TREND ======
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_spending = {}
    
    for month in range(1, 13):
        month_total = transaction_qs.filter(
            date__month=month,
            transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        monthly_spending[month_names[month - 1]] = float(month_total)
    
    # ====== RED FLAGS & ALERTS ======
    alerts = []
    
    # Alert 1: Over budget
    if budget_utilization_pct > 100:
        alerts.append({
            'type': 'danger',
            'icon': '⚠️',
            'title': 'Over Budget',
            'message': f'Total spending exceeds budget by ₱{float(abs(remaining_balance)):,.2f}',
            'severity': 'high'
        })
    
    # Alert 2: Approaching budget limit
    if budget_utilization_pct > 80 and budget_utilization_pct <= 100:
        alerts.append({
            'type': 'warning',
            'icon': '🔴',
            'title': 'Budget Alert',
            'message': f'Budget utilization is at {budget_utilization_pct:.1f}% - {budget_utilization_pct:.1f}% spent',
            'severity': 'high'
        })
    
    # Alert 3: Funds nearing exhaustion
    for fund in funds_data:
        if fund['utilization'] > 95:
            alerts.append({
                'type': 'warning',
                'icon': '⚠️',
                'title': f'{fund["name"]} Fund Nearly Depleted',
                'message': f'{fund["utilization"]:.1f}% utilized - Only ₱{fund["remaining"]:,.2f} remaining',
                'severity': 'medium'
            })
    
    # Alert 4: No recent transactions
    latest_transactions = transaction_qs.order_by('-date')[:1]
    if latest_transactions:
        from datetime import timedelta
        last_trans_date = latest_transactions[0].date
        days_since = (now().date() - last_trans_date).days
        if days_since > 30:
            alerts.append({
                'type': 'info',
                'icon': 'ℹ️',
                'title': 'No Recent Transactions',
                'message': f'Last transaction was {days_since} days ago',
                'severity': 'low'
            })
    
    # ====== PERFORMANCE METRICS ======
    # Average spending per month
    max_month = MasterFundMonitoring.objects.filter(
        date__year=year_filter
    ).aggregate(max_month=Count('date__month', distinct=True))['max_month'] or 12
    
    # Calculate how many months have data
    months_with_data = sum(1 for v in monthly_spending.values() if v > 0)
    monthly_average = float(net_disbursement) / months_with_data if months_with_data > 0 else 0
    
    # Payment efficiency: transactions per month
    transaction_count = transaction_qs.count()
    monthly_transaction_avg = transaction_count / max_month if max_month > 0 else 0
    
    # Total downloads
    total_downloads = transaction_qs.aggregate(total=Sum('downloads'))['total'] or Decimal(0)
    
    performance_metrics = {
        'total_transactions': transaction_count,
        'total_downloads': float(total_downloads),
        'avg_monthly_spending': monthly_average,
        'monthly_transaction_avg': round(monthly_transaction_avg, 1),
    }
    
    # ====== PREPARE CONTEXT ======
    context = {
        # High-level metrics
        'total_budget': float(total_budget),
        'net_disbursement': float(net_disbursement),
        'remaining_balance': float(remaining_balance),
        'budget_utilization_pct': round(budget_utilization_pct, 1),
        'budget_status': budget_status,
        'status_label': status_label,
        'status_color': status_color,
        
        # Fund breakdown
        'funds_data': funds_data,
        'funds_data_json': json.dumps(funds_data),
        
        # Charts
        'monthly_spending': json.dumps(monthly_spending),
        
        # Alerts & Performance
        'alerts': alerts,
        'performance_metrics': performance_metrics,
        
        # Filter options
        'years': sorted(transaction_years),
        'current_year': year_filter,
        'selected_year': str(year_filter),
    }
    
    return render(request, 'executive_dashboard.html', context)
