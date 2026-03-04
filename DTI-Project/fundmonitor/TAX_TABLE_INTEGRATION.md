# Tax Table Integration with Master Fund Monitoring

## Implementation Summary

This document outlines the implementation of automatic tax calculation based on purchase type selection in the Master Fund Monitoring form.

### Overview
Users selecting a purchase type from the dropdown will now have the tax breakdown fields automatically populated based on the tax rates defined in the Tax Table, proportional to the payment amount entered.

**Example:**
- Payment entered: ₱33,330.12
- Purchase type selected: VGoods (Goods VAT)
- System fetches tax rates for VGoods from the Tax Table
- Calculates and populates:
  - Goods 5%: ₱1,487.95 (payment × 0.05)
  - Services 5%: ₱0 (not applicable)
  - Goods 1%: ₱297.59 (payment × 0.01)
  - etc.

---

## What Was Changed

### 1. **Model Updates** (`dashboard_app/models/funding.py`)

**MasterFundMonitoring.purchase_type**
- Changed from `CharField` to `ForeignKey` to `PurchaseType` model
- This links fund monitoring records to the actual purchase types defined in the system
- Removed: Max length 100 character limit
- Added: Relationship to PurchaseType with SET_NULL on deletion (allows null values)

```python
# OLD (CharField)
purchase_type = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="Type of purchase"
)

# NEW (ForeignKey)
purchase_type = models.ForeignKey(
    'PurchaseType',
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='monitoring_records',
    help_text="Type of purchase with associated tax rates"
)
```

### 2. **Form Updates** (`dashboard_app/forms/funding.py`)

**MasterFundMonitoringForm.purchase_type widget**
- Changed from TextInput to Select (dropdown)
- Now properly bound to the PurchaseType model's queryset
- Django automatically handles the dropdown with all active purchase types

```python
# OLD
'purchase_type': forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Type of purchase'
}),

# NEW
'purchase_type': forms.Select(attrs={
    'class': 'form-control',
    'id': 'purchaseTypeSelect'
}),
```

### 3. **API Endpoints** (`dashboard_app/views/funding.py`)

**New Endpoint: `get_tax_rates(request, purchase_type_id)`**
- Returns tax rates for a specific purchase type
- Response format:
```json
{
    "vat_goods_5": 0.05,
    "vat_services_5": 0.05,
    "vat_goods_services_3": 0.03,
    "vat_goods_1": 0.01,
    "vat_services_2": 0.02,
    "vat_rental_5": 0.05,
    "vat_prof_fee_10": 0.10
}
```

**URL Route:** `/api/tax_rates/<purchase_type_id>/`

### 4. **URL Configuration** (`fundmonitor/urls.py`)

Added URL pattern:
```python
path('api/tax_rates/<int:purchase_type_id>/', views.get_tax_rates, name='get_tax_rates'),
```

### 5. **Template Updates** (`dashboard_app/templates/funding/master_fund_monitoring_form.html`)

**Added Second Tax Breakdown Section**
- Previously only had the first set of tax breakdown fields
- Now includes the complete second set:
  - Goods (5%) (2)
  - Services (5%) (2)
  - Goods/Services (1%)
  - Goods (1%) (2)
  - Services (2%) (2)
  - Rental (5%) (2)

**Enhanced JavaScript**

The form now includes intelligent JavaScript that:

1. **Listens for Purchase Type Changes**
   - When user selects a purchase type from the dropdown
   - Fetches tax rates from `/api/tax_rates/<purchase_type_id>/`

2. **Auto-calculates Tax Amounts**
   - Multiplies payment amount by each tax rate
   - Populates all 7 tax breakdown fields
   - Formula: `Tax Amount = Payment Amount × Tax Rate`

3. **Listens for Payment Changes**
   - If payment amount is changed after selecting purchase type
   - Automatically recalculates all tax amounts
   - Real-time updates as user types

4. **Maintains Existing Functionality**
   - Still auto-populates TIN from supplier
   - Still auto-populates Tax Type from supplier VAT status
   - Now also pulls tax rates and calculates breakdowns

### 6. **Database Migration** (`dashboard_app/migrations/0037_alter_masterfundmonitoring_purchase_type.py`)

Created migration to:
- Remove the old CharField `purchase_type` field
- Add new ForeignKey `purchase_type` field
- Safely applied with `SET_NULL` on deletion

---

## How It Works - User Experience

### Flow:

1. **User opens Master Fund Monitoring Form**
   - See purchase_type dropdown with all active purchase types

2. **User selects a Purchase Type**
   - e.g., "VGoods" (Goods VAT)

3. **System automatically:**
   - Fetches tax rates for "VGoods" from Tax Table
   - If payment amount is already entered, calculates taxes
   - Populates all tax breakdown fields

4. **User enters Payment Amount**
   - e.g., ₱33,330.12

5. **System:**
   - Recalculates all tax amounts based on payment
   - Updates fields in real-time

### Example Tax Calculation:

**Scenario:** VGoods Purchase Type with ₱33,330.12 payment

Tax rates from Tax Table for VGoods:
- Goods (5%): 0.05 → ₱33,330.12 × 0.05 = **₱1,666.51**
- Services (5%): 0.05 → ₱33,330.12 × 0.05 = **₱1,666.51**
- Goods & Services (3%): 0.03 → ₱33,330.12 × 0.03 = **₱999.90**
- Goods (1%): 0.01 → ₱33,330.12 × 0.01 = **₱333.30**
- Services (2%): 0.02 → ₱33,330.12 × 0.02 = **₱666.60**
- Rental (5%): 0.05 → ₱33,330.12 × 0.05 = **₱1,666.51**
- Prof. Fee (10%): 0.10 → ₱33,330.12 × 0.10 = **₱3,333.01**

All fields are auto-filled, ready for submission.

---

## Files Modified

1. ✅ `dashboard_app/models/funding.py` - Changed purchase_type to ForeignKey
2. ✅ `dashboard_app/forms/funding.py` - Changed widget to Select dropdown
3. ✅ `dashboard_app/views/funding.py` - Added new `get_tax_rates()` API endpoint
4. ✅ `dashboard_app/views/__init__.py` - Exported `get_tax_rates`
5. ✅ `fundmonitor/urls.py` - Added URL route for tax_rates API
6. ✅ `dashboard_app/migrations/0037_alter_masterfundmonitoring_purchase_type.py` - Database migration
7. ✅ `dashboard_app/templates/funding/master_fund_monitoring_form.html` - Enhanced form template with:
   - Added second tax breakdown section
   - Enhanced JavaScript for auto-calculation

---

## API Reference

### Get Tax Rates by Purchase Type

**Endpoint:** `GET /api/tax_rates/<purchase_type_id>/`

**Parameters:**
- `purchase_type_id` (integer, required) - ID of the PurchaseType

**Success Response (200 OK):**
```json
{
    "vat_goods_5": 0.05,
    "vat_services_5": 0.05,
    "vat_goods_services_3": 0.03,
    "vat_goods_1": 0.01,
    "vat_services_2": 0.02,
    "vat_rental_5": 0.05,
    "vat_prof_fee_10": 0.10
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Tax rates not found for this purchase type"
}
```

---

## Testing the Feature

1. **Admin Panel:**
   - Go to `/admin/dashboard_app/taxtable/`
   - Verify tax rates are configured for purchase types

2. **Fund Monitoring Form:**
   - Go to `/master_fund_monitoring/add/`
   - Select a purchase type from dropdown
   - Verify dropdown appears correctly

3. **Auto-calculation:**
   - Enter a payment amount
   - Select a purchase type
   - Verify all tax breakdown fields populate automatically
   - Change payment amount
   - Verify taxes recalculate

4. **Browser Console:**
   - Check developer console for any errors
   - Look for success messages: "Tax rates applied for purchase type: X"

---

## Troubleshooting

### Tax fields not populating?
1. Check that tax rates are configured in Tax Table for the selected purchase type
2. Verify payment amount is entered and greater than 0
3. Check browser console for API errors
4. Ensure `/api/tax_rates/<id>/` endpoint is accessible

### Purchase type dropdown not showing?
1. Verify purchase types exist in database
2. Ensure `is_active` is True for purchase types
3. Check form render - should be `<select>` element

### API returning 404?
1. Verify purchase_type_id is correct
2. Ensure TaxTable entry exists for that PurchaseType
3. Check database for orphaned purchase types

---

## Future Enhancements

- Add formula support in Tax Table fields (e.g., "=vat_goods_5 + vat_goods_1")
- Implement tax configuration profiles (e.g., "Standard VAT", "Simplified Tax")
- Add report generation for tax compliance
- Batch tax recalculation for historical records
- Tax audit trail logging

---

## Database State

- Migration 0037 has been applied
- MasterFundMonitoring.purchase_type is now a ForeignKey
- All existing CharField purchase_type data must be manually migrated if needed
- Tax Table configuration from migration 0036 is in use

