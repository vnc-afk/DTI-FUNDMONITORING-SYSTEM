"""Master Fund Monitoring Views - CRUD operations for fund monitoring records"""

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.urls import reverse
from dashboard_app.models import MasterFundMonitoring
from dashboard_app.forms import MasterFundMonitoringForm


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
    return render(request, 'funding/master_fund_monitoring/master_fund_monitoring.html', context)


def master_fund_monitoring_create(request):
    """Create new master fund monitoring record"""
    if request.method == 'POST':
        form = MasterFundMonitoringForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('master_fund_monitoring_list')
    else:
        form = MasterFundMonitoringForm()

    return render(request, 'funding/master_fund_monitoring/master_fund_monitoring_form.html', {'form': form})


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

    return render(request, 'funding/master_fund_monitoring/master_fund_monitoring_form.html', {'form': form})


def master_fund_monitoring_delete(request, pk):
    """Delete master fund monitoring record"""
    record = get_object_or_404(MasterFundMonitoring, pk=pk)
    
    if request.method == 'POST':
        record.delete()
        return redirect('master_fund_monitoring_list')
    
    # Build object details for the template
    object_details = {
        'Payee': record.payee,
        'Date': record.date.strftime('%b %d, %Y'),
        'Amount': f"₱ {record.payments:,.2f}",
        'Fund Source': record.fund_source,
    }
    
    context = {
        'object_type': 'Fund Monitoring Record',
        'back_url': reverse('master_fund_monitoring_list'),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)
