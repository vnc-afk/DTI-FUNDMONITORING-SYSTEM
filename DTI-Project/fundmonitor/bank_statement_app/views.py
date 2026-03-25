import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from user_app.utils import get_items_per_page

from .forms import BankStatementForm
from .models import BankStatement


@login_required
def bank_statement_list(request):
    query = (request.GET.get("q") or "").strip()
    status_filter = (request.GET.get("status") or "").strip()
    page_size = get_items_per_page(request)

    statements_qs = BankStatement.objects.all().order_by("-date", "-created_at")

    if query:
        statements_qs = statements_qs.filter(
            Q(description__icontains=query)
            | Q(check_number__icontains=query)
        )

    if status_filter in {"Cleared", "On Process"}:
        statements_qs = statements_qs.filter(status=status_filter)

    statement_count = statements_qs.count()
    totals = statements_qs.aggregate(total_debits=Sum("debit"), total_credits=Sum("credit"))
    
    total_debits = totals["total_debits"] or 0
    total_credits = totals["total_credits"] or 0

    # "Current" cards should show the latest running amounts, not aggregates.
    latest_statement = BankStatement.objects.all().order_by("-date", "-created_at").first()
    current_debit = latest_statement.debit if latest_statement and latest_statement.debit else 0
    current_credit = latest_statement.credit if latest_statement and latest_statement.credit else 0
    current_balance = latest_statement.balance if latest_statement and latest_statement.balance else 0

    per_page = statement_count if status_filter else page_size
    paginator = Paginator(statements_qs, max(per_page, 1))
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "statements": page_obj.object_list,
        "page_obj": page_obj,
        "statement_count": statement_count,
        "toolbar_count": f"{statement_count} entr{'y' if statement_count == 1 else 'ies'}",
        "status_filter": status_filter,
        "status_filter_options": [
            {"value": "On Process", "label": "On Process"},
            {"value": "Cleared", "label": "Cleared"},
        ],
        "total_debits": total_debits,
        "total_credits": total_credits,
        "summary_cards": [
            {"title": "Current Debit", "value": current_debit, "icon": "arrow-down", "description": "Most recent debit", "css_class": "text-danger"},
            {"title": "Current Credit", "value": current_credit, "icon": "arrow-up", "description": "Most recent credit", "css_class": "text-success"},
            {"title": "Current Balance", "value": current_balance, "icon": "wallet", "description": "Latest running balance", "css_class": "text-primary"},
        ],
    }
    return render(request, "bank_statement_app/funding/bank_statement/bank_statement.html", context)


@login_required
def bank_statement_create(request):
    is_first_transaction = not BankStatement.objects.exists()
    previous_balance = 0

    if not is_first_transaction:
        last_transaction = BankStatement.objects.order_by('-date', '-created_at').first()
        previous_balance = last_transaction.balance if last_transaction else 0

    if request.method == "POST":
        form = BankStatementForm(request.POST, is_first_transaction=is_first_transaction)
        if form.is_valid():
            form.save()
            return redirect("bank_statement_list")
    else:
        form = BankStatementForm(is_first_transaction=is_first_transaction)

    return render(
        request,
        "bank_statement_app/funding/bank_statement/bank_statement_form.html",
        {"form": form, "is_edit": False, "is_first_transaction": is_first_transaction, "previous_balance": previous_balance},
    )


@login_required
def bank_statement_update(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)
    previous_transaction = BankStatement.objects.exclude(pk=statement.pk).order_by('-date', '-created_at').first()
    previous_balance = previous_transaction.balance if previous_transaction else 0

    if request.method == "POST":
        form = BankStatementForm(request.POST, instance=statement, is_first_transaction=False)
        if form.is_valid():
            form.save()
            return redirect("bank_statement_list")
    else:
        form = BankStatementForm(instance=statement, is_first_transaction=False)

    return render(
        request,
        "bank_statement_app/funding/bank_statement/bank_statement_form.html",
        {
            "form": form,
            "statement": statement,
            "is_edit": True,
            "is_first_transaction": False,
            "previous_balance": previous_balance,
        },
    )


@login_required
def bank_statement_delete(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)
    statement.delete()
    return redirect("bank_statement_list")


@login_required
@require_POST
def bank_statement_update_status(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    status = payload.get("status")
    if status not in {"Cleared", "On Process"}:
        return JsonResponse({"success": False, "message": "Invalid status."}, status=400)

    statement.status = status
    statement.save(update_fields=["status", "updated_at"])
    return JsonResponse({"success": True})


@login_required
@require_POST
def bank_statement_bulk_delete(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        payload = {}

    ids = payload.get("ids") or []
    if not isinstance(ids, list):
        return JsonResponse({"success": False, "message": "Invalid payload."}, status=400)

    deleted_count, _ = BankStatement.objects.filter(id__in=ids).delete()
    return JsonResponse({"success": True, "deleted_count": deleted_count})


__all__ = [
    "bank_statement_list",
    "bank_statement_create",
    "bank_statement_update",
    "bank_statement_delete",
    "bank_statement_update_status",
    "bank_statement_bulk_delete",
]
