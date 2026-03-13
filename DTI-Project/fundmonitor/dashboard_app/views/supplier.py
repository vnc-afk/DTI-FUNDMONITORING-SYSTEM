from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
from dashboard_app.models import Supplier
from dashboard_app.forms import SupplierForm


def supplier_list(request):
    """List all suppliers with search support"""
    all_suppliers = Supplier.objects.all()
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_suppliers = all_suppliers.filter(
            Q(supplier__icontains=search_query) |
            Q(tin__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(propprietor__icontains=search_query) |
            Q(contact_number__icontains=search_query) |
            Q(philgeps_registration__icontains=search_query)
        )
    
    supplier_count = all_suppliers.count()
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        suppliers = all_suppliers
        paginator = None
    else:
        paginator = Paginator(all_suppliers, 50)
        page_number = request.GET.get('page', 1)
        suppliers = paginator.get_page(page_number)
    
    vat_v_count = Supplier.objects.filter(vat_status='V').count()
    vat_nv_count = Supplier.objects.filter(vat_status='NV').count()
    
    # Prepare summary cards for component
    summary_cards = [
        {
            'label': 'Total Suppliers',
            'value': supplier_count,
            'sublabel': 'All suppliers',
            'is_currency': False,
        },
        {
            'label': 'VAT Registered',
            'value': vat_v_count,
            'sublabel': 'Registered suppliers',
            'is_currency': False,
        },
        {
            'label': 'Non-VAT Registered',
            'value': vat_nv_count,
            'sublabel': 'Non registered suppliers',
            'is_currency': False,
        }
    ]
    
    # Prepare filter options for component
    vat_filter_options = {
        'V': 'Registered',
        'NV': 'Non-Registered'
    }
    
    # Prepare toolbar count
    toolbar_count = f'{supplier_count} supplier{"" if supplier_count == 1 else "s"}'
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = suppliers
    
    context = {
        'suppliers': suppliers,
        'supplier_count': supplier_count,
        'vat_v_count': vat_v_count,
        'vat_nv_count': vat_nv_count,
        'summary_cards': summary_cards,
        'vat_filter_options': vat_filter_options,
        'toolbar_count': toolbar_count,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
    }
    return render(request, 'supplier/supplier_list.html', context)


def supplier_add(request):
    """Add new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'supplier/supplier_form.html', {'form': form})


def supplier_edit(request, pk):
    """Edit existing supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'supplier/supplier_form.html', {'form': form})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')
    
    object_details = {
        'Name': supplier.supplier,
        'TIN': supplier.tin,
        'VAT Status': supplier.get_vat_status_display(),
        'PHILGEPS': supplier.philgeps_registration,
        'Address': supplier.address,
        'Proprietor': supplier.propprietor,
        'Contact': supplier.contact_number or '—',       
    }
    
    context = {
        'object_type': 'Supplier',
        'item_label': supplier.supplier,
        'item_name': 'supplier',
        'back_url': reverse('supplier_list'),
        'delete_url': reverse('supplier_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)


@require_http_methods(["POST"])
def supplier_bulk_delete(request):
    """Delete multiple suppliers via AJAX"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'success': False, 'message': 'No ids provided'})
        
        # Ensure ids are integers
        ids = [int(id) for id in ids]
        
        # Delete the suppliers
        deleted_count, _ = Supplier.objects.filter(pk__in=ids).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} supplier(s) deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)