"""API Views - Helper functions for AJAX requests and data retrieval"""

import re
from django.http import JsonResponse
from dashboard_app.models import Supplier, TaxTable


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
        return JsonResponse({'error': 'Tax rates not found for this purchase type'}, status=404)
