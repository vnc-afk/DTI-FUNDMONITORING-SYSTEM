from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
from dashboard_app.models import FundSource, BankStatement, MasterFundMonitoring, Supplier, FundSourceBreakdown
from dashboard_app.forms import FundSourceForm, BankStatementForm, MasterFundMonitoringForm, FundSourceBreakdownForm


# Fund Source Views

def fund_sources_view(request):
    """List all fund sources with statistics"""
    funds = FundSource.objects.all()
    
    # Calculate totals
    total_budget = funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    fund_count = funds.count()
    average_budget = total_budget / fund_count if fund_count > 0 else 0
    
    context = {
        'funds': funds,
        'total_budget': total_budget,
        'fund_count': fund_count,
        'average_budget': average_budget,
    }
    return render(request, 'funding/fund_sources.html', context)


def fund_source_create(request):
    """Create new fund source"""
    if request.method == 'POST':
        form = FundSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm()

    return render(request, 'funding/fund_source_form.html', {'form': form})


def fund_source_update(request, pk):
    """Update existing fund source"""
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == 'POST':
        form = FundSourceForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm(instance=fund)

    return render(request, 'funding/fund_source_form.html', {'form': form})


def fund_source_delete(request, pk):
    """Delete fund source"""
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == 'POST':
        fund.delete()
        return redirect('fund_sources')

    return render(request, 'funding/fund_source_confirm_delete.html', {'fund': fund})


def fund_source_detail(request, pk):
    """View fund source details including breakdowns"""
    fund = get_object_or_404(FundSource, pk=pk)
    breakdowns = fund.breakdowns.all()
    total_breakdown = breakdowns.aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    over_budget_amount = max(0, total_breakdown - fund.annual_budget)
    
    context = {
        'fund': fund,
        'breakdowns': breakdowns,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
        'over_budget_amount': over_budget_amount,
    }
    return render(request, 'funding/fund_source_detail.html', context)


def fund_source_breakdown_add(request, fund_id):
    """Add breakdown for a fund source"""
    fund = get_object_or_404(FundSource, pk=fund_id)
    total_breakdown = fund.breakdowns.aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    
    if request.method == 'POST':
        form = FundSourceBreakdownForm(request.POST, fund_source=fund)
        if form.is_valid():
            breakdown = form.save(commit=False)
            breakdown.fund_source = fund
            breakdown.save()
            return redirect('fund_source_detail', pk=fund_id)
    else:
        form = FundSourceBreakdownForm(fund_source=fund)
    
    context = {
        'fund': fund,
        'form': form,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
    }
    return render(request, 'funding/fund_source_breakdown_form.html', context)


def fund_source_breakdown_edit(request, pk):
    """Edit breakdown for a fund source"""
    breakdown = get_object_or_404(FundSourceBreakdown, pk=pk)
    fund = breakdown.fund_source
    total_breakdown = fund.breakdowns.exclude(id=pk).aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    
    if request.method == 'POST':
        form = FundSourceBreakdownForm(request.POST, instance=breakdown, fund_source=fund)
        if form.is_valid():
            form.save()
            return redirect('fund_source_detail', pk=fund.id)
    else:
        form = FundSourceBreakdownForm(instance=breakdown, fund_source=fund)
    
    context = {
        'fund': fund,
        'breakdown': breakdown,
        'form': form,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
    }
    return render(request, 'funding/fund_source_breakdown_form.html', context)


def fund_source_breakdown_delete(request, pk):
    """Delete breakdown for a fund source"""
    breakdown = get_object_or_404(FundSourceBreakdown, pk=pk)
    fund_id = breakdown.fund_source.id
    
    if request.method == 'POST':
        breakdown.delete()
        return redirect('fund_source_detail', pk=fund_id)
    
    context = {
        'breakdown': breakdown,
        'fund': breakdown.fund_source,
    }
    return render(request, 'funding/fund_source_breakdown_confirm_delete.html', context)


# Bank Statement Views

def bank_statement_list(request):
    """List all bank statements with statistics"""
    statements = BankStatement.objects.all().order_by('-date', '-created_at')
    
    # Calculate totals
    debits = statements.filter(debit__gt=0).aggregate(total=Sum('debit'))['total'] or 0
    credits = statements.filter(credit__gt=0).aggregate(total=Sum('credit'))['total'] or 0
    
    # Get latest statement for current values (by date and creation time)
    latest_statement = statements.first()
    current_debit = latest_statement.debit if latest_statement else 0
    current_credit = latest_statement.credit if latest_statement else 0
    current_balance = latest_statement.balance if latest_statement else 0
    
    context = {
        'statements': statements,
        'total_debits': debits,
        'total_credits': credits,
        'statement_count': statements.count(),
        'current_debit': current_debit,
        'current_credit': current_credit,
        'current_balance': current_balance,
    }
    return render(request, 'funding/bank_statement.html', context)


def bank_statement_create(request):
    """Create new bank statement"""
    # Check if there are existing transactions
    has_existing = BankStatement.objects.exists()
    previous_balance = 0
    
    if has_existing:
        # Get the last transaction's balance
        last_statement = BankStatement.objects.order_by('-date', '-created_at').first()
        previous_balance = float(last_statement.balance) if last_statement else 0
    
    if request.method == 'POST':
        form = BankStatementForm(request.POST, is_first_transaction=not has_existing)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(is_first_transaction=not has_existing)
    
    context = {
        'form': form,
        'is_first_transaction': not has_existing,
        'previous_balance': previous_balance,
    }
    return render(request, 'funding/bank_statement_form.html', context)


def bank_statement_update(request, pk):
    """Update existing bank statement"""
    statement = get_object_or_404(BankStatement, pk=pk)

    # For updates, always show as not first transaction (readonly)
    # Get the previous transaction's balance (before this one)
    previous_balance = 0
    transactions_before = BankStatement.objects.exclude(id=pk).order_by('-date', '-created_at')
    
    if transactions_before.exists():
        last_before = transactions_before.first()
        previous_balance = float(last_before.balance) if last_before else 0

    if request.method == 'POST':
        form = BankStatementForm(request.POST, instance=statement, is_first_transaction=False)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(instance=statement, is_first_transaction=False)
    
    context = {
        'form': form,
        'is_first_transaction': False,
        'previous_balance': previous_balance,
    }
    return render(request, 'funding/bank_statement_form.html', context)


def bank_statement_delete(request, pk):
    """Delete bank statement"""
    statement = get_object_or_404(BankStatement, pk=pk)

    if request.method == 'POST':
        statement.delete()
        return redirect('bank_statement_list')

    return render(request, 'funding/bank_statement_confirm_delete.html', {'statement': statement})


# Master Fund Monitoring Views

def master_fund_monitoring_list(request):
    """List all master fund monitoring records with statistics"""
    records = MasterFundMonitoring.objects.all().order_by('-date')
    
    # Calculate totals
    total_payments = records.aggregate(total=Sum('payments'))['total'] or 0
    
    context = {
        'records': records,
        'total_payments': total_payments,
        'record_count': records.count(),
    }
    return render(request, 'funding/master_fund_monitoring.html', context)


def master_fund_monitoring_create(request):
    """Create new master fund monitoring record"""
    if request.method == 'POST':
        form = MasterFundMonitoringForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('master_fund_monitoring_list')
    else:
        form = MasterFundMonitoringForm()

    return render(request, 'funding/master_fund_monitoring_form.html', {'form': form})


def master_fund_monitoring_update(request, pk):
    """Update existing master fund monitoring record"""
    record = get_object_or_404(MasterFundMonitoring, pk=pk)

    if request.method == 'POST':
        form = MasterFundMonitoringForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('master_fund_monitoring_list')
    else:
        form = MasterFundMonitoringForm(instance=record)

    return render(request, 'funding/master_fund_monitoring_form.html', {'form': form})


def master_fund_monitoring_delete(request, pk):
    """Delete master fund monitoring record"""
    record = get_object_or_404(MasterFundMonitoring, pk=pk)

    if request.method == 'POST':
        record.delete()
        return redirect('master_fund_monitoring_list')

    return render(request, 'funding/master_fund_monitoring_confirm_delete.html', {'record': record})


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
