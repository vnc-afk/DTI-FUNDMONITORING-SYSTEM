"""Master Fund Monitoring Views - CRUD operations for fund monitoring records"""

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Q
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from dashboard_app.models import MasterFundMonitoring
from dashboard_app.forms import MasterFundMonitoringForm


def master_fund_monitoring_list(request):
    """List all master fund monitoring records with statistics and search support"""
    all_records = MasterFundMonitoring.objects.all().order_by('-date')
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_records = all_records.filter(
            Q(payee__icontains=search_query) |
            Q(particulars__icontains=search_query) |
            Q(fund_source__name__icontains=search_query) |
            Q(cheque_number__icontains=search_query) |
            Q(date__icontains=search_query)
        )
    
    # Calculate totals - ensure it's always a numeric value
    total_result = all_records.aggregate(total=Sum('payments'))['total']
    total_payments = float(total_result) if total_result is not None else 0.0
    
    record_count = all_records.count()
    
    # Prepare filter options for component
    cheque_status_filter_options = {
        'pending': 'Pending',
        'cleared': 'Cleared',
        'bounced': 'Bounced',
    }
    
    # Prepare toolbar count
    toolbar_count = f'{record_count} entr{"y" if record_count == 1 else "ies"}'
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        records = all_records
        paginator = None
    else:
        paginator = Paginator(all_records, 50)
        page_number = request.GET.get('page', 1)
        records = paginator.get_page(page_number)
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = records
    
    context = {
        'records': records,
        'total_payments': total_payments,
        'record_count': record_count,
        'cheque_status_filter_options': cheque_status_filter_options,
        'toolbar_count': toolbar_count,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
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
        'item_label': f"{record.payee} - {record.date.strftime('%b %d, %Y')}",
        'item_name': 'fund monitoring record',
        'back_url': reverse('master_fund_monitoring_list'),
        'delete_url': reverse('master_fund_monitoring_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)


@require_http_methods(["POST"])
def master_fund_monitoring_bulk_delete(request):
    """Delete multiple master fund monitoring records via AJAX"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'success': False, 'message': 'No ids provided'})
        
        # Ensure ids are integers
        ids = [int(id) for id in ids]
        
        # Delete the records
        deleted_count, _ = MasterFundMonitoring.objects.filter(pk__in=ids).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} record(s) deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
