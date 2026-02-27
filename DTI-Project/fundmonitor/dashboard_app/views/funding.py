from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import JsonResponse
from dashboard_app.models import FundSource, BankStatement, MasterFundMonitoring, Supplier
from dashboard_app.forms import FundSourceForm, BankStatementForm, MasterFundMonitoringForm


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


# Bank Statement Views

def bank_statement_list(request):
    """List all bank statements with statistics"""
    statements = BankStatement.objects.all().order_by('-date')
    
    # Calculate totals
    debits = statements.filter(debit__gt=0).aggregate(total=Sum('debit'))['total'] or 0
    credits = statements.filter(credit__gt=0).aggregate(total=Sum('credit'))['total'] or 0
    
    context = {
        'statements': statements,
        'total_debits': debits,
        'total_credits': credits,
        'statement_count': statements.count(),
    }
    return render(request, 'funding/bank_statement.html', context)


def bank_statement_create(request):
    """Create new bank statement"""
    if request.method == 'POST':
        form = BankStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm()

    return render(request, 'funding/bank_statement_form.html', {'form': form})


def bank_statement_update(request, pk):
    """Update existing bank statement"""
    statement = get_object_or_404(BankStatement, pk=pk)

    if request.method == 'POST':
        form = BankStatementForm(request.POST, instance=statement)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(instance=statement)

    return render(request, 'funding/bank_statement_form.html', {'form': form})


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
    total_downloads = records.aggregate(total=Sum('downloads'))['total'] or 0
    
    context = {
        'records': records,
        'total_payments': total_payments,
        'total_downloads': total_downloads,
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
