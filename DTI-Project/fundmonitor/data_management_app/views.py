import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from dashboard_app.views.api import get_fund_budget, get_supplier_data, get_tax_rates
from user_app.utils import get_items_per_page

from .forms import (
    ExpenseCategoryForm,
    ExpenseObjectForm,
    FundSourceBreakdownForm,
    FundSourceForm,
    StaffForm,
    SupplierForm,
    TaxTableForm,
)
from .models import BreakdownCategory, ExpenseCategory, ExpenseObject, FundSource, FundSourceBreakdown, Staff, Supplier, TaxTable


@login_required
def fund_sources_view(request):
    query = (request.GET.get("q") or "").strip()
    page_size = get_items_per_page(request)

    funds_qs = FundSource.objects.all().order_by("name")
    if query:
        funds_qs = funds_qs.filter(name__icontains=query)

    fund_count = funds_qs.count()
    total_budget = funds_qs.aggregate(total=Sum("annual_budget"))["total"] or 0
    active_fund_count = funds_qs.filter(annual_budget__gt=0).count()

    paginator = Paginator(funds_qs, max(page_size, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "funds": page_obj.object_list,
        "page_obj": page_obj,
        "fund_count": fund_count,
        "fund_count_text": f"{fund_count} fund{'s' if fund_count != 1 else ''}",
        "total_budget": total_budget,
        "active_fund_count": active_fund_count,
        "summary_cards": [
            {"title": "Total Fund Sources", "value": fund_count, "icon": "wallet2", "description": "All sources"},
            {"title": "Total Budget", "value": total_budget, "icon": "cash", "description": "Annual allocation"},
            {"title": "Active Funds", "value": active_fund_count, "icon": "check-circle", "description": "With budget"},
        ],
    }
    return render(request, "data_management_app/funding/fund_source/fund_sources.html", context)


@login_required
def fund_source_create(request):
    if request.method == "POST":
        form = FundSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("fund_sources")
    else:
        form = FundSourceForm()

    return render(request, "data_management_app/funding/fund_source/fund_source_form.html", {"form": form})


@login_required
def fund_source_update(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == "POST":
        form = FundSourceForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect("fund_sources")
    else:
        form = FundSourceForm(instance=fund)

    return render(request, "data_management_app/funding/fund_source/fund_source_form.html", {"form": form, "fund": fund})


@login_required
def fund_source_delete(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)
    fund.delete()
    return redirect("fund_sources")


@login_required
def fund_source_detail(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)
    breakdowns = FundSourceBreakdown.objects.filter(fund_source=fund).select_related("category").order_by("category__order", "category__code")

    total_breakdown = breakdowns.aggregate(total=Sum("budget_amount"))["total"] or 0
    remaining_budget = (fund.annual_budget or 0) - total_breakdown
    over_budget_amount = abs(remaining_budget) if remaining_budget < 0 else 0

    used_category_ids = breakdowns.values_list("category_id", flat=True)
    available_count = BreakdownCategory.objects.filter(is_active=True).exclude(id__in=used_category_ids).count()

    context = {
        "fund": fund,
        "breakdowns": breakdowns,
        "total_breakdown": total_breakdown,
        "remaining_budget": max(remaining_budget, 0),
        "over_budget_amount": over_budget_amount,
        "all_categories_allocated": available_count == 0,
        "summary_cards": [
            {"title": "Annual Budget", "value": fund.annual_budget or 0, "icon": "cash", "description": "Total fund budget"},
            {"title": "Allocated", "value": total_breakdown, "icon": "pie-chart", "description": "To categories"},
            {"title": "Remaining", "value": max(remaining_budget, 0), "icon": "wallet2", "description": "Unallocated"},
        ],
    }
    return render(request, "data_management_app/funding/fund_source/fund_source_detail.html", context)


@login_required
def fund_source_breakdown_add(request, fund_id):
    fund = get_object_or_404(FundSource, pk=fund_id)
    used_category_ids = FundSourceBreakdown.objects.filter(fund_source=fund).values_list("category_id", flat=True)

    if request.method == "POST":
        form = FundSourceBreakdownForm(request.POST, fund_source=fund)
        form.fields["category"].queryset = BreakdownCategory.objects.filter(is_active=True).exclude(id__in=used_category_ids)
        if form.is_valid():
            breakdown = form.save(commit=False)
            breakdown.fund_source = fund
            breakdown.save()
            return redirect("fund_source_detail", pk=fund.id)
    else:
        form = FundSourceBreakdownForm(fund_source=fund)
        form.fields["category"].queryset = BreakdownCategory.objects.filter(is_active=True).exclude(id__in=used_category_ids)

    remaining_budget = (fund.annual_budget or 0) - (FundSourceBreakdown.objects.filter(fund_source=fund).aggregate(total=Sum("budget_amount"))["total"] or 0)

    return render(
        request,
        "data_management_app/funding/fund_source/fund_source_breakdown_form.html",
        {"form": form, "fund": fund, "remaining_budget": max(remaining_budget, 0)},
    )


@login_required
def fund_source_breakdown_edit(request, pk):
    breakdown = get_object_or_404(FundSourceBreakdown.objects.select_related("fund_source"), pk=pk)
    fund = breakdown.fund_source

    if request.method == "POST":
        form = FundSourceBreakdownForm(request.POST, instance=breakdown, fund_source=fund)
        if form.is_valid():
            form.save()
            return redirect("fund_source_detail", pk=fund.id)
    else:
        form = FundSourceBreakdownForm(instance=breakdown, fund_source=fund)

    other_total = FundSourceBreakdown.objects.filter(fund_source=fund).exclude(pk=breakdown.pk).aggregate(total=Sum("budget_amount"))["total"] or 0
    remaining_budget = (fund.annual_budget or 0) - other_total

    return render(
        request,
        "data_management_app/funding/fund_source/fund_source_breakdown_form.html",
        {"form": form, "fund": fund, "remaining_budget": max(remaining_budget, 0)},
    )


@login_required
@require_POST
def fund_source_breakdown_delete(request, pk):
    breakdown = get_object_or_404(FundSourceBreakdown.objects.select_related("fund_source"), pk=pk)
    fund_id = breakdown.fund_source_id
    breakdown.delete()
    return redirect("fund_source_detail", pk=fund_id)


@login_required
def tax_table_list(request):
    tax_entries = TaxTable.objects.select_related("purchase_type").order_by("purchase_type__name")
    page_size = get_items_per_page(request)
    paginator = Paginator(tax_entries, max(page_size, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "entries": page_obj.object_list,
        "page_obj": page_obj,
        "entry_count": tax_entries.count(),
    }
    return render(request, "data_management_app/tax/tax_table.html", context)


@login_required
def tax_table_create(request):
    if request.method == "POST":
        form = TaxTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("tax_table")
    else:
        form = TaxTableForm()

    return render(request, "data_management_app/tax/tax_form.html", {"form": form})


@login_required
def tax_table_update(request, pk):
    entry = get_object_or_404(TaxTable, pk=pk)

    if request.method == "POST":
        form = TaxTableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("tax_table")
    else:
        form = TaxTableForm(instance=entry)

    return render(request, "data_management_app/tax/tax_form.html", {"form": form, "entry": entry})


@login_required
def tax_table_delete(request, pk):
    entry = get_object_or_404(TaxTable, pk=pk)
    entry.delete()
    return redirect("tax_table")


@login_required
def staff_list(request):
    query = (request.GET.get("q") or "").strip()
    division_filter = (request.GET.get("status") or "").strip()
    page_size = get_items_per_page(request)

    staff_qs = Staff.objects.select_related("division").order_by("last_name", "first_name")
    if query:
        staff_qs = staff_qs.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(middle_initial__icontains=query)
            | Q(division__name__icontains=query)
        )
    if division_filter:
        staff_qs = staff_qs.filter(division__name=division_filter)

    staff_count = staff_qs.count()
    divisions_count = staff_qs.values("division_id").distinct().count()

    per_page = staff_count if division_filter else page_size
    paginator = Paginator(staff_qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    division_options = (
        Staff.objects.select_related("division")
        .exclude(division__isnull=True)
        .values_list("division__name", flat=True)
        .distinct()
        .order_by("division__name")
    )

    context = {
        "staff_members": page_obj.object_list,
        "page_obj": page_obj,
        "staff_count": staff_count,
        "divisions_count": divisions_count,
        "toolbar_count": f"{staff_count} entr{'y' if staff_count == 1 else 'ies'}",
        "division_filter": division_filter,
        "division_filter_options": [{"value": name, "label": name} for name in division_options],
        "summary_cards": [
            {"title": "Staff Members", "value": staff_count, "icon": "people", "description": "Total employees"},
            {"title": "Divisions", "value": divisions_count, "icon": "building", "description": "Active departments"},
        ],
    }
    return render(request, "data_management_app/staff/staff_list.html", context)


@login_required
def staff_add(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff")
    else:
        form = StaffForm()

    return render(request, "data_management_app/staff/staff_form.html", {"form": form})


@login_required
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == "POST":
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect("staff")
    else:
        form = StaffForm(instance=staff)

    return render(request, "data_management_app/staff/staff_form.html", {"form": form, "staff": staff})


@login_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.delete()
    return redirect("staff")


@login_required
@require_POST
def staff_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = Staff.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


@login_required
def expense_object_list(request):
    query = (request.GET.get("q") or "").strip()
    status_filter = (request.GET.get("status") or "").strip().lower()
    page_size = get_items_per_page(request)

    objects_qs = ExpenseObject.objects.all().order_by("code")
    if query:
        objects_qs = objects_qs.filter(Q(code__icontains=query) | Q(name__icontains=query) | Q(description__icontains=query))
    if status_filter == "active":
        objects_qs = objects_qs.filter(is_active=True)
    elif status_filter == "inactive":
        objects_qs = objects_qs.filter(is_active=False)

    object_count = objects_qs.count()
    active_count = objects_qs.filter(is_active=True).count()

    per_page = object_count if status_filter else page_size
    paginator = Paginator(objects_qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "expense_objects": page_obj.object_list,
        "page_obj": page_obj,
        "object_count": object_count,
        "toolbar_count": f"{object_count} entr{'y' if object_count == 1 else 'ies'}",
        "status_filter": status_filter,
        "status_filter_options": [
            {"value": "active", "label": "Active"},
            {"value": "inactive", "label": "Inactive"},
        ],
        "summary_cards": [
            {"title": "Expense Objects", "value": object_count, "icon": "card-text", "description": "All items"},
            {"title": "Active", "value": active_count, "icon": "check-circle", "description": "In use"},
        ],
    }
    return render(request, "data_management_app/expense_object/expense_object_list.html", context)


@login_required
def expense_object_add(request):
    if request.method == "POST":
        form = ExpenseObjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("expense_object_list")
    else:
        form = ExpenseObjectForm()

    return render(request, "data_management_app/expense_object/expense_object_form.html", {"form": form})


@login_required
def expense_object_edit(request, pk):
    expense_object = get_object_or_404(ExpenseObject, pk=pk)

    if request.method == "POST":
        form = ExpenseObjectForm(request.POST, instance=expense_object)
        if form.is_valid():
            form.save()
            return redirect("expense_object_list")
    else:
        form = ExpenseObjectForm(instance=expense_object)

    return render(request, "data_management_app/expense_object/expense_object_form.html", {"form": form, "expense_object": expense_object})


@login_required
def expense_object_delete(request, pk):
    expense_object = get_object_or_404(ExpenseObject, pk=pk)
    expense_object.delete()
    return redirect("expense_object_list")


@login_required
@require_POST
def expense_object_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = ExpenseObject.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


@login_required
def expense_category_list(request):
    query = (request.GET.get("q") or "").strip()
    status_filter = (request.GET.get("status") or "").strip().lower()
    page_size = get_items_per_page(request)

    categories_qs = ExpenseCategory.objects.all().order_by("name")
    if query:
        categories_qs = categories_qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if status_filter == "active":
        categories_qs = categories_qs.filter(is_active=True)
    elif status_filter == "inactive":
        categories_qs = categories_qs.filter(is_active=False)

    category_count = categories_qs.count()
    active_count = categories_qs.filter(is_active=True).count()

    per_page = category_count if status_filter else page_size
    paginator = Paginator(categories_qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "expense_categories": page_obj.object_list,
        "page_obj": page_obj,
        "category_count": category_count,
        "toolbar_count": f"{category_count} entr{'y' if category_count == 1 else 'ies'}",
        "status_filter": status_filter,
        "status_filter_options": [
            {"value": "active", "label": "Active"},
            {"value": "inactive", "label": "Inactive"},
        ],
        "summary_cards": [
            {"title": "Categories", "value": category_count, "icon": "collection", "description": "All categories"},
            {"title": "Active", "value": active_count, "icon": "check-circle", "description": "In use"},
        ],
    }
    return render(request, "data_management_app/expense_category/expense_category_list.html", context)


@login_required
def expense_category_add(request):
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("expense_category_list")
    else:
        form = ExpenseCategoryForm()

    return render(request, "data_management_app/expense_category/expense_category_form.html", {"form": form})


@login_required
def expense_category_edit(request, pk):
    expense_category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST, instance=expense_category)
        if form.is_valid():
            form.save()
            return redirect("expense_category_list")
    else:
        form = ExpenseCategoryForm(instance=expense_category)

    return render(request, "data_management_app/expense_category/expense_category_form.html", {"form": form, "expense_category": expense_category})


@login_required
def expense_category_delete(request, pk):
    expense_category = get_object_or_404(ExpenseCategory, pk=pk)
    expense_category.delete()
    return redirect("expense_category_list")


@login_required
@require_POST
def expense_category_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = ExpenseCategory.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


@login_required
def supplier_list(request):
    query = (request.GET.get("q") or "").strip()
    vat_status_filter = (request.GET.get("status") or "").strip()
    page_size = get_items_per_page(request)

    # Calculate summary card totals from ALL suppliers (unfiltered)
    total_suppliers = Supplier.objects.all().count()
    vat_registered_count = Supplier.objects.filter(vat_status='V').count()
    non_vat_count = Supplier.objects.filter(vat_status='NV').count()
    na_count = Supplier.objects.filter(vat_status='—').count()

    suppliers_qs = Supplier.objects.all().order_by("supplier")
    if query:
        suppliers_qs = suppliers_qs.filter(
            Q(supplier__icontains=query)
            | Q(tin__icontains=query)
            | Q(philgeps_registration__icontains=query)
            | Q(address__icontains=query)
            | Q(propprietor__icontains=query)
            | Q(contact_number__icontains=query)
        )
    if vat_status_filter in {"V", "NV", "—"}:
        suppliers_qs = suppliers_qs.filter(vat_status=vat_status_filter)

    supplier_count = suppliers_qs.count()

    per_page = supplier_count if vat_status_filter else page_size
    paginator = Paginator(suppliers_qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "suppliers": page_obj.object_list,
        "page_obj": page_obj,
        "supplier_count": supplier_count,
        "toolbar_count": f"{supplier_count} entr{'y' if supplier_count == 1 else 'ies'}",
        "vat_status_filter": vat_status_filter,
        "vat_filter_options": [
            {"value": "V", "label": "VAT Registered"},
            {"value": "NV", "label": "Non-VAT"},
            {"value": "—", "label": "N/A"},
        ],
        "summary_cards": [
            {"title": "VAT Registered", "value": vat_registered_count, "icon": "percent", "description": "With VAT", "css_class": "text-success"},
            {"title": "Non-VAT Registered", "value": non_vat_count, "icon": "percent", "description": "Without VAT", "css_class": "text-warning"},
            {"title": "N/A", "value": na_count, "icon": "question-circle", "description": "No status", "css_class": "text-danger"},
        ],
    }
    return render(request, "data_management_app/supplier/supplier_list.html", context)


@login_required
def supplier_add(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm()

    return render(request, "data_management_app/supplier/supplier_form.html", {"form": form})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, "data_management_app/supplier/supplier_form.html", {"form": form, "supplier": supplier})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    return redirect("supplier_list")


@login_required
@require_POST
def supplier_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = Supplier.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


__all__ = [
    "fund_sources_view",
    "fund_source_create",
    "fund_source_update",
    "fund_source_delete",
    "fund_source_detail",
    "fund_source_breakdown_add",
    "fund_source_breakdown_edit",
    "fund_source_breakdown_delete",
    "tax_table_list",
    "tax_table_create",
    "tax_table_update",
    "tax_table_delete",
    "staff_list",
    "staff_add",
    "staff_edit",
    "staff_delete",
    "staff_bulk_delete",
    "expense_object_list",
    "expense_object_add",
    "expense_object_edit",
    "expense_object_delete",
    "expense_object_bulk_delete",
    "expense_category_list",
    "expense_category_add",
    "expense_category_edit",
    "expense_category_delete",
    "expense_category_bulk_delete",
    "supplier_list",
    "supplier_add",
    "supplier_edit",
    "supplier_delete",
    "supplier_bulk_delete",
    "get_supplier_data",
    "get_tax_rates",
    "get_fund_budget",
]
