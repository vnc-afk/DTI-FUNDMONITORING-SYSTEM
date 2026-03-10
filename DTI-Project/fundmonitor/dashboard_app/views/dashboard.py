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
    year_filter = request.GET.get('year', current_year)
    
    # Build filter dictionary
    filters = {}
    if request.GET.get('year'):
        filters['date__year'] = int(request.GET.get('year'))
    else:
        filters['date__year'] = current_year
    
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
    
    # Calculate refunds (which reduce the disbursement)
    refund_qs = transaction_qs.filter(transaction_type='Refund')
    total_refunds = refund_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Calculate adjustments (treated as disbursements for now)
    adjustment_qs = transaction_qs.filter(transaction_type='Adjustment')
    total_adjustments = adjustment_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Remaining balance = Total Budget - Disbursements - Adjustments + Refunds
    remaining_balance = total_budget - total_disbursement - total_adjustments + total_refunds
    
    # Budget utilization rate is based on net disbursement (disbursements + adjustments - refunds)
    net_disbursement = total_disbursement + total_adjustments - total_refunds
    budget_utilization_rate = (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    total_transactions = transaction_qs.count()
    total_suppliers_paid = transaction_qs.values('payee').distinct().count()
    
    # ====== 2. MONTHLY DISBURSEMENT TREND ======
    monthly_data = {}
    for month in range(1, 13):
        month_sum = transaction_qs.filter(date__month=month).aggregate(
            total=Sum('payments')
        )['total'] or Decimal(0)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_data[month_names[month - 1]] = float(month_sum)
    
    # ====== 3. REMAINING AVAILABLE BY FUND SOURCE (DONUT) ======
    fund_remaining = []
    for fs in FundSource.objects.all():
        disbursed = transaction_qs.filter(fund_source=fs).aggregate(
            total=Sum('payments')
        )['total'] or Decimal(0)
        remaining = fs.annual_budget - disbursed
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
        disburse = transaction_qs.filter(fund_source=fs).aggregate(
            total=Sum('payments')
        )['total'] or Decimal(0)
        budget_vs_disburse.append({
            'name': fs.name,
            'budget': float(fs.annual_budget),
            'disbursed': float(disburse)
        })
    
    budget_labels = [item['name'] for item in budget_vs_disburse]
    budget_amounts = [item['budget'] for item in budget_vs_disburse]
    disburse_amounts = [item['disbursed'] for item in budget_vs_disburse]
    
    # ====== 5. ACCOUNT TITLE / EXPENSE OBJECTS ANALYSIS (HORIZONTAL BAR) ======
    expense_analysis = transaction_qs.values(
        'account_title__name'
    ).annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    expense_labels = [item['account_title__name'] or 'Unspecified' for item in expense_analysis]
    expense_values = [float(item['total'] or 0) for item in expense_analysis]
    
    # ====== 6. TOP SUPPLIERS / PAYEES (BAR CHART - TOP 10) ======
    top_suppliers = transaction_qs.values('payee__supplier').annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    supplier_labels = [item['payee__supplier'] or 'Unspecified' for item in top_suppliers]
    supplier_values = [float(item['total'] or 0) for item in top_suppliers]
    
    # ====== 7. TAX WITHHOLDING SUMMARY (STACKED BAR) ======
    tax_summary = transaction_qs.aggregate(
        goods_5=Sum('goods_5_percent'),
        services_5=Sum('services_5_percent'),
        goods_services_3=Sum('goods_services_3_percent'),
        goods_1=Sum('goods_1_percent'),
        services_2=Sum('services_2_percent'),
        rental_5=Sum('rental_5_percent'),
        prof_fee_10=Sum('prof_fee_10_percent'),
    )
    
    tax_labels = ['Goods (5%)', 'Services (5%)', 'Goods & Services (3%)',
                  'Goods (1%)', 'Services (2%)', 'Rental (5%)', 'Prof Fee (10%)']
    tax_values = [
        float(tax_summary['goods_5'] or 0),
        float(tax_summary['services_5'] or 0),
        float(tax_summary['goods_services_3'] or 0),
        float(tax_summary['goods_1'] or 0),
        float(tax_summary['services_2'] or 0),
        float(tax_summary['rental_5'] or 0),
        float(tax_summary['prof_fee_10'] or 0),
    ]
    
    # ====== 8. CHEQUE MONITORING (DONUT) ======
    cheque_status = transaction_qs.values('cheque_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    cheque_labels = [item['cheque_status'] or 'Unknown' for item in cheque_status]
    cheque_counts = [item['count'] for item in cheque_status]
    
    # ====== 9. DISTRICT SPENDING (STACKED COLUMN) ======
    district_spending = transaction_qs.values(
        'nc__district__name'
    ).annotate(
        total=Sum('payments')
    ).order_by('-total')
    
    district_labels = [item['nc__district__name'] or 'Unspecified' for item in district_spending]
    district_values = [float(item['total'] or 0) for item in district_spending]
    
    # ====== 10. BANK BALANCE TREND (AREA CHART) ======
    bank_statements = BankStatement.objects.filter(
        date__year=filters.get('date__year', current_year)
    ).order_by('date')
    
    bank_dates = [str(stmt.date) for stmt in bank_statements]
    bank_debits = [float(stmt.debit or 0) for stmt in bank_statements]
    bank_credits = [float(stmt.credit or 0) for stmt in bank_statements]
    bank_balances = [float(stmt.balance or 0) for stmt in bank_statements]
    
    # ====== FILTER OPTIONS ======
    years = sorted(set(MasterFundMonitoring.objects.dates('date', 'year')))
    years = [dt.year for dt in years]
    
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
        'fund_labels': json.dumps(fund_labels),
        'fund_values': json.dumps(fund_values),
        'budget_labels': json.dumps(budget_labels),
        'budget_amounts': json.dumps(budget_amounts),
        'disburse_amounts': json.dumps(disburse_amounts),
        'expense_labels': json.dumps(expense_labels),
        'expense_values': json.dumps(expense_values),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'tax_labels': json.dumps(tax_labels),
        'tax_values': json.dumps(tax_values),
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
        'current_year': int(year_filter) if year_filter and year_filter != '' else current_year,
        
        # Current filter values (for preserving selections)
        'selected_year': request.GET.get('year', ''),
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
