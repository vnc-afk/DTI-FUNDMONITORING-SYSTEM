import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from user_app.utils import get_items_per_page

from dashboard_app.views.api import get_mooe_budget

from .forms import MasterFundMonitoringForm
from .models import MasterFundMonitoring


@login_required
def master_fund_monitoring_list(request):
    query = (request.GET.get("q") or "").strip()
    cheque_status_filter = (request.GET.get("status") or "").strip()
    page_size = get_items_per_page(request)

    records_qs = MasterFundMonitoring.objects.all().select_related(
        "fund_source", "payee", "division", "nc", "staff", "purchase_type", "account_title", "expense_classification"
    ).order_by("-date", "-id")

    if query:
        records_qs = records_qs.filter(
            Q(particulars__icontains=query)
            | Q(payee__supplier__icontains=query)
            | Q(fund_source__name__icontains=query)
            | Q(cheque_number__icontains=query)
        )

    if cheque_status_filter in {"Pending", "Cleared"}:
        records_qs = records_qs.filter(cheque_status=cheque_status_filter)

    record_count = records_qs.count()
    totals = records_qs.aggregate(total_payments=Sum("payments"), total_downloads=Sum("downloads"))

    paginator = Paginator(records_qs, max(page_size, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "records": page_obj.object_list,
        "page_obj": page_obj,
        "record_count": record_count,
        "toolbar_count": f"{record_count} entr{'y' if record_count == 1 else 'ies'}",
        "cheque_status_filter": cheque_status_filter,
        "cheque_status_filter_options": [
            {"value": "Pending", "label": "Pending"},
            {"value": "Cleared", "label": "Cleared"},
        ],
        "total_payments": totals["total_payments"] or 0,
        "total_downloads": totals["total_downloads"] or 0,
    }
    return render(
        request,
        "mater_fundmonitor_app/funding/master_fund_monitoring/master_fund_monitoring.html",
        context,
    )


@login_required
def master_fund_monitoring_create(request):
    if request.method == "POST":
        form = MasterFundMonitoringForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("master_fund_monitoring_list")
    else:
        form = MasterFundMonitoringForm()

    return render(
        request,
        "mater_fundmonitor_app/funding/master_fund_monitoring/master_fund_monitoring_form.html",
        {"form": form, "is_edit": False},
    )


@login_required
def master_fund_monitoring_update(request, pk):
    record = get_object_or_404(MasterFundMonitoring, pk=pk)

    if request.method == "POST":
        form = MasterFundMonitoringForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("master_fund_monitoring_list")
    else:
        form = MasterFundMonitoringForm(instance=record)

    return render(
        request,
        "mater_fundmonitor_app/funding/master_fund_monitoring/master_fund_monitoring_form.html",
        {"form": form, "record": record, "is_edit": True},
    )


@login_required
def master_fund_monitoring_delete(request, pk):
    record = get_object_or_404(MasterFundMonitoring, pk=pk)
    record.delete()
    return redirect("master_fund_monitoring_list")


@login_required
@require_POST
def master_fund_monitoring_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = MasterFundMonitoring.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


__all__ = [
    "master_fund_monitoring_list",
    "master_fund_monitoring_create",
    "master_fund_monitoring_update",
    "master_fund_monitoring_delete",
    "master_fund_monitoring_bulk_delete",
    "get_mooe_budget",
]
