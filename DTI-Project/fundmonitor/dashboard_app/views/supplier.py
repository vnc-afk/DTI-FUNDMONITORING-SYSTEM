from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from dashboard_app.models import Supplier
from dashboard_app.forms import SupplierForm


def supplier_list(request):
    """List all suppliers"""
    suppliers = Supplier.objects.all()
    supplier_count = suppliers.count()
    vat_v_count = suppliers.filter(vat_status='V').count()
    vat_nv_count = suppliers.filter(vat_status='NV').count()
    
    context = {
        'suppliers': suppliers,
        'supplier_count': supplier_count,
        'vat_v_count': vat_v_count,
        'vat_nv_count': vat_nv_count,
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
        'back_url': reverse('supplier_list'),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)