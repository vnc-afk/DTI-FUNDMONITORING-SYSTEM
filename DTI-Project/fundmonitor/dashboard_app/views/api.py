"""API Views - Helper functions for AJAX requests and data retrieval"""

import re
from django.http import JsonResponse
from django.db.models import Sum
from data_management_app.models import Supplier, TaxTable, FundSource, BreakdownCategory, FundSourceBreakdown
from mater_fundmonitor_app.models import MasterFundMonitoring


def get_supplier_data(request, supplier_id):
    """API endpoint to get supplier TIN and VAT status for auto-population"""
    try:
        supplier = Supplier.objects.get(pk=supplier_id)
        data = {
            'tin': supplier.tin,
            'vat_status': supplier.vat_status,
        }
        return JsonResponse(data)
    except Supplier.DoesNotExist:
        return JsonResponse({'error': 'Supplier not found'}, status=404)


def parse_tax_rate(value):
    """
    Parse tax rate value - can be:
    - A formula string like "=0.05/1.12"
    - A numeric string like "0.05"
    - An empty string or None
    """
    if value is None or value == '':
        return None
    
    value = str(value).strip()
    
    if not value:
        return None
    
    # Check if it's a formula (starts with =)
    if value.startswith('='):
        try:
            # Remove the = sign and evaluate
            formula = value[1:]
            # Sanitize - only allow numbers, operators, parentheses, decimal points
            if not re.match(r'^[0-9+\-*/%().\s]+$', formula):
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
                {'error': 'Purchase type ID is required', 'status': 'error'},
                status=400
            )
        
        tax_entry = TaxTable.objects.get(purchase_type_id=purchase_type_id)
        
        data = {
            'vat_goods_5': parse_tax_rate(tax_entry.vat_goods_5),
            'vat_services_5': parse_tax_rate(tax_entry.vat_services_5),
            'vat_goods_services_3': parse_tax_rate(tax_entry.vat_goods_services_3),
            'vat_goods_1': parse_tax_rate(tax_entry.vat_goods_1),
            'vat_services_2': parse_tax_rate(tax_entry.vat_services_2),
            'vat_rental_5': parse_tax_rate(tax_entry.vat_rental_5),
            'vat_prof_fee_10': parse_tax_rate(tax_entry.vat_prof_fee_10),
        }
        return JsonResponse(data)
    except TaxTable.DoesNotExist:
        return JsonResponse(
            {'error': f'Tax rates not configured for purchase type {purchase_type_id}. Please set up tax rules in the Tax Table.', 'status': 'error'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': f'Error retrieving tax rates: {str(e)}', 'status': 'error'},
            status=500
        )


def get_fund_budget(request):
    """API endpoint to get budget information for a fund source"""
    fund_id = request.GET.get('fund_id')
    
    if not fund_id:
        return JsonResponse({'error': 'Fund ID is required'}, status=400)
    
    try:
        fund = FundSource.objects.get(pk=fund_id)
        
        # Calculate total disbursements for this fund
        total_disbursed = MasterFundMonitoring.objects.filter(
            fund_source=fund,
            transaction_type='Disbursement'
        ).aggregate(total=Sum('payments'))['total'] or 0
        
        # Calculate total refunds for this fund (refunds reduce the net disbursed amount)
        total_refunded = MasterFundMonitoring.objects.filter(
            fund_source=fund,
            transaction_type='Refund'
        ).aggregate(total=Sum('payments'))['total'] or 0
        
        # Calculate total downloads (fund allocations from higher office via MDP)
        total_downloads = MasterFundMonitoring.objects.filter(
            fund_source=fund
        ).aggregate(total=Sum('downloads'))['total'] or 0
        
        # Net disbursed = disbursements minus refunds
        net_disbursed = total_disbursed - total_refunded
        
        # Total available = annual budget + downloads - net disbursed
        total_available = (fund.annual_budget or 0) + total_downloads
        available = total_available - net_disbursed
        
        data = {
            'id': fund.id,
            'name': fund.name,
            'annual_budget': float(fund.annual_budget or 0),
            'total_downloads': float(total_downloads),
            'total_available': float(total_available),
            'total_disbursed': float(total_disbursed),
            'total_refunded': float(total_refunded),
            'net_disbursed': float(net_disbursed),
            'available': float(available),
        }
        return JsonResponse(data)
    except FundSource.DoesNotExist:
        return JsonResponse({'error': 'Fund source not found'}, status=404)


def get_mooe_budget(request):
    """API endpoint to get budget information for a MOOE category"""
    mooe_id = request.GET.get('mooe_id')
    
    if not mooe_id:
        return JsonResponse({'error': 'MOOE ID is required'}, status=400)
    
    try:
        mooe = BreakdownCategory.objects.get(pk=mooe_id)
        
        # Calculate annual budget for this MOOE category (sum of all fund source breakdowns)
        annual_budget = FundSourceBreakdown.objects.filter(
            category=mooe
        ).aggregate(total=Sum('budget_amount'))['total'] or 0
        
        # Calculate total disbursements for this MOOE category
        total_disbursed = MasterFundMonitoring.objects.filter(
            mooe=mooe.code,
            transaction_type='Disbursement'
        ).aggregate(total=Sum('payments'))['total'] or 0
        
        # Calculate total refunds for this MOOE category (refunds reduce the net disbursed amount)
        total_refunded = MasterFundMonitoring.objects.filter(
            mooe=mooe.code,
            transaction_type='Refund'
        ).aggregate(total=Sum('payments'))['total'] or 0
        
        # Calculate total downloads for this MOOE category
        total_downloads = MasterFundMonitoring.objects.filter(
            mooe=mooe.code
        ).aggregate(total=Sum('downloads'))['total'] or 0
        
        # Net disbursed = disbursements minus refunds
        net_disbursed = total_disbursed - total_refunded
        
        # Total available = annual budget + downloads - net disbursed
        total_available = annual_budget + total_downloads
        available = total_available - net_disbursed
        
        data = {
            'id': mooe.id,
            'code': mooe.code,
            'name': mooe.name,
            'annual_budget': float(annual_budget),
            'total_downloads': float(total_downloads),
            'total_available': float(total_available),
            'total_disbursed': float(total_disbursed),
            'total_refunded': float(total_refunded),
            'net_disbursed': float(net_disbursed),
            'available': float(available),
        }
        return JsonResponse(data)
    except BreakdownCategory.DoesNotExist:
        return JsonResponse({'error': 'MOOE category not found'}, status=404)


# ============================================================================
# DASHBOARD DATA API ENDPOINTS - For AJAX loading without full page reload
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from decimal import Decimal
import json


@login_required
def get_dashboard_kpis(request):
    """
    API endpoint to get dashboard KPI data without rendering full page
    Returns: JSON with KPI summary cards data
    """
    # Get filter parameters from request
    filters = {}
    year = request.GET.get('year')
    filters['date__year'] = int(year) if year and year.isdigit() else now().year
    
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
    
    transaction_qs = MasterFundMonitoring.objects.filter(**filters)
    
    total_budget = FundSource.objects.aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
    all_fund_sources = FundSource.objects.all()
    active_funds = all_fund_sources.filter(annual_budget__gt=0)
    
    disbursement_qs = transaction_qs.filter(transaction_type='Disbursement')
    total_disbursement = disbursement_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    downloads_qs = transaction_qs.filter(transaction_type='Downloads')
    total_downloads = downloads_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    refund_qs = transaction_qs.filter(transaction_type='Refund')
    total_refunds = refund_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    adjustment_qs = transaction_qs.filter(transaction_type='Adjustment')
    total_adjustments = adjustment_qs.aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    remaining_balance = total_budget - total_disbursement - total_downloads - total_adjustments + total_refunds
    net_disbursement = total_disbursement + total_downloads + total_adjustments - total_refunds
    budget_util_rate = (float(net_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    
    return JsonResponse({
        'totalBudget': float(total_budget),
        'activeFunds': active_funds.count(),
        'activeBudget': float(active_funds.aggregate(total=Sum('annual_budget'))['total'] or 0),
        'totalDisbursement': float(total_disbursement),
        'totalDownloads': float(total_downloads),
        'totalRefunds': float(total_refunds),
        'totalAdjustments': float(total_adjustments),
        'remainingBalance': float(remaining_balance),
        'budgetUtilizationRate': budget_util_rate,
        'totalTransactions': transaction_qs.count(),
        'totalSuppliersPaid': transaction_qs.values('payee').distinct().count(),
    })


@login_required
def get_dashboard_charts(request):
    """
    API endpoint to get all dashboard chart data
    Returns: JSON with all chart data (monthly trends, fund breakdown, etc.)
    """
    from django.db.models import Count, Q, F
    
    # Get filter parameters
    filters = {}
    year = request.GET.get('year')
    filters['date__year'] = int(year) if year and year.isdigit() else now().year
    
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
    
    transaction_qs = MasterFundMonitoring.objects.filter(**filters)
    
    # Monthly trends
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = {}
    for month in range(1, 13):
        month_sum = transaction_qs.filter(
            date__month=month,
            transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        monthly_data[month_names[month - 1]] = float(month_sum)
    
    # Fund source breakdown
    fund_remaining = []
    for fs in FundSource.objects.all():
        disbursed = transaction_qs.filter(fund_source=fs, transaction_type__in=['Disbursement', 'Downloads', 'Adjustment']).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        refunded = transaction_qs.filter(fund_source=fs, transaction_type='Refund').aggregate(total=Sum('payments'))['total'] or Decimal(0)
        downloads_amt = transaction_qs.filter(fund_source=fs).aggregate(total=Sum('downloads'))['total'] or Decimal(0)
        net_disbursed = disbursed - refunded
        remaining = fs.annual_budget + downloads_amt - net_disbursed
        if remaining > 0:
            fund_remaining.append({'name': fs.name, 'remaining': float(remaining)})
    
    fund_remaining.sort(key=lambda x: x['remaining'], reverse=True)
    
    # Expense classification breakdown
    from data_management_app.models import ExpenseCategory
    expense_breakdown = []
    for exp_cat in ExpenseCategory.objects.all():
        total = transaction_qs.filter(expense_category=exp_cat).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        if total > 0:
            expense_breakdown.append({'name': exp_cat.name, 'value': float(total)})
    
    expense_breakdown.sort(key=lambda x: x['value'], reverse=True)
    
    return JsonResponse({
        'monthlyData': monthly_data,
        'fundBreakdown': [f['name'] for f in fund_remaining],
        'fundValues': [f['remaining'] for f in fund_remaining],
        'expenseLabels': [e['name'] for e in expense_breakdown],
        'expenseValues': [e['value'] for e in expense_breakdown],
    })


@login_required
def get_dashboard_filters(request):
    """
    API endpoint to get available filter options
    Returns: JSON with all filter dropdown options
    """
    from data_management_app.models import District, Division, ExpenseCategory
    
    return JsonResponse({
        'years': sorted(set(MasterFundMonitoring.objects.values_list('date__year', flat=True))),
        'fundSources': [{'id': fs.id, 'name': fs.name} for fs in FundSource.objects.all()],
        'divisions': [{'id': d.id, 'name': d.name} for d in Division.objects.all()],
        'districts': [{'id': d.id, 'name': d.name} for d in District.objects.all()],
        'expenseCategories': [{'id': ec.id, 'name': ec.name} for ec in ExpenseCategory.objects.all()],
        'suppliers': [{'id': s.id, 'name': s.name} for s in Supplier.objects.all().order_by('name')[:1000]],
    })
