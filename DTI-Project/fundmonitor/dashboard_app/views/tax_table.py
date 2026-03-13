"""Tax Table Views - CRUD operations for tax rates"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from dashboard_app.models import TaxTable
from dashboard_app.forms import TaxTableForm


def tax_table_list(request):
    """List all tax table entries with search support"""
    all_entries = TaxTable.objects.all()
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_entries = all_entries.filter(
            Q(purchase_type__name__icontains=search_query)
        )
    
    count = all_entries.count()
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        entries = all_entries
        paginator = None
    else:
        paginator = Paginator(all_entries, 50)
        page_number = request.GET.get('page', 1)
        entries = paginator.get_page(page_number)
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = entries
    
    context = {
        'entries': entries,
        'entry_count': count,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
    }
    return render(request, 'funding/tax/tax_table.html', context)



def tax_table_create(request):
    """Create new tax table entry"""
    if request.method == 'POST':
        form = TaxTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tax_table')
    else:
        form = TaxTableForm()
    return render(request, 'funding/tax/tax_form.html', {'form': form})


def tax_table_update(request, pk):
    """Update existing tax table entry"""
    entry = get_object_or_404(TaxTable, pk=pk)
    if request.method == 'POST':
        form = TaxTableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('tax_table')
    else:
        form = TaxTableForm(instance=entry)
    return render(request, 'funding/tax/tax_form.html', {'form': form})


def tax_table_delete(request, pk):
    tax_table = get_object_or_404(TaxTable, pk=pk)
    
    if request.method == 'POST':
        tax_table.delete()
        return redirect('tax_table_list')
    
    object_details = {
        'Purchase Type': tax_table.purchase_type.name if tax_table.purchase_type else 'N/A',
        'VAT Goods (5%)': tax_table.vat_goods_5 or 'N/A',
        'VAT Services (5%)': tax_table.vat_services_5 or 'N/A',
        'VAT Goods & Services (3%)': tax_table.vat_goods_services_3 or 'N/A',
        'VAT Goods (1%)': tax_table.vat_goods_1 or 'N/A',
        'VAT Services (2%)': tax_table.vat_services_2 or 'N/A',
        'VAT Rental (5%)': tax_table.vat_rental_5 or 'N/A',
        'VAT Professional Fee (10%)': tax_table.vat_prof_fee_10 or 'N/A',       
    }
    
    context = {
        'object_type': 'Tax Table Entry',
        'item_label': f"Tax Table: {tax_table.purchase_type.name if tax_table.purchase_type else 'N/A'}",
        'item_name': 'tax table entry',
        'back_url': reverse('tax_table'),
        'delete_url': reverse('tax_table_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)