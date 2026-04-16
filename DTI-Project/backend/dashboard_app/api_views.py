from datetime import timedelta

from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, Q, Sum
from django.utils.timezone import now
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from bank_statement_app.models import BankStatement
from dashboard_app.views.import_data import _log_import_activity, process_import
from data_management_app.forms import ImportDataForm
from mater_fundmonitor_app.models import MasterFundMonitoring
from user_app.utils import get_items_per_page

from .models import ActivityLog, Notification
from .serializers import ActivityLogSerializer, NotificationSerializer
from .utils.archive_utils import (
    archive_by_year,
    get_archive_stats,
    get_archive_year_statuses,
    get_archive_years,
    unarchive_by_year,
)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return ActivityLog.objects.none()

        queryset = (
            ActivityLog.objects.select_related("user")
            .prefetch_related("user__groups")
            .all()
            .order_by("-timestamp")
        )

        action_value = (self.request.query_params.get("action") or "").strip()
        user_value = (self.request.query_params.get("user") or "").strip()
        model_value = (self.request.query_params.get("model") or "").strip()
        date_value = (self.request.query_params.get("date") or "").strip()
        search_value = (self.request.query_params.get("search") or "").strip()

        if action_value:
            queryset = queryset.filter(action=action_value)

        if user_value.isdigit():
            queryset = queryset.filter(user_id=int(user_value))

        if model_value:
            queryset = queryset.filter(model_name=model_value)

        if date_value == "today":
            queryset = queryset.filter(timestamp__date=now().date())
        elif date_value == "week":
            queryset = queryset.filter(timestamp__gte=now() - timedelta(days=7))
        elif date_value == "month":
            queryset = queryset.filter(timestamp__gte=now() - timedelta(days=30))

        if search_value:
            queryset = queryset.filter(
                Q(object_repr__icontains=search_value)
                | Q(description__icontains=search_value)
                | Q(user__username__icontains=search_value)
                | Q(user__first_name__icontains=search_value)
                | Q(user__last_name__icontains=search_value)
            )

        return queryset

    @action(detail=False, methods=["get"], url_path="filters")
    def filters(self, request):
        if not request.user.is_superuser:
            return Response(
                {
                    "actions": [
                        {"code": code, "name": name}
                        for code, name in ActivityLog.ACTION_CHOICES
                    ],
                    "users": [],
                    "models": [],
                }
            )

        model_name = (request.query_params.get("model") or "").strip()

        users = User.objects.filter(activity_logs__isnull=False)
        if model_name:
            users = users.filter(activity_logs__model_name=model_name)
        users = users.distinct().order_by("username")

        models = (
            ActivityLog.objects.values_list("model_name", flat=True)
            .distinct()
            .order_by("model_name")
        )

        return Response(
            {
                "actions": [
                    {"code": code, "name": name}
                    for code, name in ActivityLog.ACTION_CHOICES
                ],
                "users": [
                    {
                        "id": user.id,
                        "display_name": (user.get_full_name() or "").strip()
                        or user.username,
                    }
                    for user in users
                ],
                "models": list(models),
            }
        )

    @action(detail=False, methods=["get"], url_path=r"user/(?P<user_id>[^/.]+)")
    def user_logs(self, request, user_id=None):
        try:
            target_user_id = int(user_id or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid user id."}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.id != target_user_id and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to view these logs."},
                status=status.HTTP_403_FORBIDDEN,
            )

        viewed_user = User.objects.filter(id=target_user_id).first()
        if not viewed_user:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        queryset = (
            ActivityLog.objects.select_related("user")
            .prefetch_related("user__groups")
            .filter(user_id=target_user_id)
            .order_by("-timestamp")
        )

        action_value = (request.query_params.get("action") or "").strip()
        date_value = (request.query_params.get("date") or "").strip()
        search_value = (request.query_params.get("search") or "").strip()

        if action_value:
            queryset = queryset.filter(action=action_value)

        if date_value == "today":
            queryset = queryset.filter(timestamp__date=now().date())
        elif date_value == "week":
            queryset = queryset.filter(timestamp__gte=now() - timedelta(days=7))
        elif date_value == "month":
            queryset = queryset.filter(timestamp__gte=now() - timedelta(days=30))

        if search_value:
            queryset = queryset.filter(
                Q(object_repr__icontains=search_value)
                | Q(description__icontains=search_value)
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["viewed_user"] = {
                "id": viewed_user.id,
                "username": viewed_user.username,
                "display_name": (viewed_user.get_full_name() or "").strip()
                or viewed_user.username,
            }
            response.data["total_logs"] = queryset.count()
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "count": queryset.count(),
                "next": None,
                "previous": None,
                "results": serializer.data,
                "viewed_user": {
                    "id": viewed_user.id,
                    "username": viewed_user.username,
                    "display_name": (viewed_user.get_full_name() or "").strip()
                    or viewed_user.username,
                },
                "total_logs": queryset.count(),
            }
        )

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        if not request.user.is_superuser:
            return Response(
                {
                    "total_logs": 0,
                    "today_logs": 0,
                    "week_logs": 0,
                    "month_logs": 0,
                    "actions_breakdown": [],
                    "modified_models": [],
                    "active_users": [],
                    "sensitive_logs": [],
                }
            )

        now_time = now()
        today = now_time.date()

        total_logs = ActivityLog.objects.count()
        today_logs = ActivityLog.objects.filter(timestamp__date=today).count()
        week_logs = ActivityLog.objects.filter(
            timestamp__gte=now_time - timedelta(days=7)
        ).count()
        month_logs = ActivityLog.objects.filter(
            timestamp__gte=now_time - timedelta(days=30)
        ).count()

        actions_breakdown = list(
            ActivityLog.objects.values("action")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        modified_models = list(
            ActivityLog.objects.values("model_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        active_users_rows = (
            ActivityLog.objects.values(
                "user_id",
                "user__username",
                "user__first_name",
                "user__last_name",
            )
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        active_users = [
            {
                "user_id": row["user_id"],
                "username": row["user__username"] or "",
                "first_name": row["user__first_name"] or "",
                "last_name": row["user__last_name"] or "",
                "display_name": f"{(row['user__first_name'] or '').strip()} {(row['user__last_name'] or '').strip()}".strip()
                or (row["user__username"] or "Unknown"),
                "count": row["count"],
            }
            for row in active_users_rows
        ]

        sensitive_qs = (
            ActivityLog.objects.filter(is_sensitive=True)
            .select_related("user")
            .order_by("-timestamp")[:10]
        )
        sensitive_logs = [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "formatted_timestamp": log.get_formatted_timestamp(),
                "user_full_name": (
                    (log.user.get_full_name() or "").strip() if log.user else ""
                )
                or (log.user.username if log.user else "Unknown"),
                "action": log.action,
                "action_display": log.get_action_display(),
                "model_name": log.model_name,
            }
            for log in sensitive_qs
        ]

        return Response(
            {
                "total_logs": total_logs,
                "today_logs": today_logs,
                "week_logs": week_logs,
                "month_logs": month_logs,
                "actions_breakdown": actions_breakdown,
                "modified_models": modified_models,
                "active_users": active_users,
                "sensitive_logs": sensitive_logs,
            }
        )


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related("actor")
            .order_by("-created_at")
        )


class ArchiveViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        return Response(
            {
                "stats": get_archive_stats(),
                "years_available": get_archive_years(),
                "year_statuses": get_archive_year_statuses(),
            }
        )

    @action(detail=False, methods=["post"], url_path="year")
    def archive_year(self, request):
        year_value = request.data.get("year")
        reason = request.data.get("reason", "")

        if year_value in (None, ""):
            return Response(
                {"error": "Year is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            year = int(year_value)
            if year < 1900 or year > 2099:
                return Response(
                    {"error": "Invalid year"}, status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid year format"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing_counts = get_archive_stats(year)
        active_total = existing_counts.get("fund_monitoring_year", {}).get(
            "active", 0
        ) + existing_counts.get("bank_statements_year", {}).get("active", 0)

        if active_total <= 0:
            return Response(
                {"error": f"No active records found for year {year}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = archive_by_year(year, user=request.user, reason=reason)
            return Response({"success": True, "result": result})
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="unarchive")
    def unarchive_year(self, request):
        year_value = request.data.get("year")

        if year_value in (None, ""):
            return Response(
                {"error": "Year is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            year = int(year_value)
            if year < 1900 or year > 2099:
                return Response(
                    {"error": "Invalid year"}, status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid year format"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing_counts = get_archive_stats(year)
        archived_total = existing_counts.get("fund_monitoring_year", {}).get(
            "archived", 0
        ) + existing_counts.get("bank_statements_year", {}).get("archived", 0)

        if archived_total <= 0:
            return Response(
                {"error": f"No archived records found for year {year}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = unarchive_by_year(year)
            return Response({"success": True, "result": result})
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="statements")
    def archived_statements(self, request):
        search_query = (request.query_params.get("q") or "").strip()
        page_size = max(int(get_items_per_page(request) or 20), 1)
        page_number = request.query_params.get("page", 1)

        queryset = (
            BankStatement.objects.all_with_archived()
            .filter(is_archived=True)
            .order_by("-archived_at")
        )

        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query)
                | Q(check_number__icontains=search_query)
                | Q(date__icontains=search_query)
            )

        total_records = queryset.count()
        total_debit_result = queryset.aggregate(total=Sum("debit"))["total"]
        total_credit_result = queryset.aggregate(total=Sum("credit"))["total"]
        total_debit = (
            float(total_debit_result) if total_debit_result is not None else 0.0
        )
        total_credit = (
            float(total_credit_result) if total_credit_result is not None else 0.0
        )

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages or 1)

        page_numbers = [
            num
            for num in paginator.page_range
            if page_obj.number - 3 <= num <= page_obj.number + 3
        ]

        results = []
        for statement in page_obj.object_list:
            results.append(
                {
                    "id": statement.id,
                    "date": statement.date.isoformat() if statement.date else None,
                    "description": statement.description or "",
                    "check_number": statement.check_number or "",
                    "debit": float(statement.debit or 0),
                    "credit": float(statement.credit or 0),
                    "balance": float(statement.balance or 0),
                    "archived_at": (
                        statement.archived_at.isoformat()
                        if statement.archived_at
                        else None
                    ),
                    "is_archived": bool(statement.is_archived),
                }
            )

        return Response(
            {
                "search_query": search_query,
                "total_records": total_records,
                "total_debit": total_debit,
                "total_credit": total_credit,
                "results": results,
                "pagination": {
                    "has_other_pages": paginator.num_pages > 1,
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(),
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "previous_page": (
                        page_obj.previous_page_number()
                        if page_obj.has_previous()
                        else None
                    ),
                    "next_page": (
                        page_obj.next_page_number() if page_obj.has_next() else None
                    ),
                    "page_numbers": page_numbers,
                },
            }
        )

    @action(
        detail=False,
        methods=["post"],
        url_path=r"statements/(?P<statement_id>[^/.]+)/restore",
    )
    def restore_statement(self, request, statement_id=None):
        try:
            target_id = int(statement_id or 0)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid statement id"}, status=status.HTTP_400_BAD_REQUEST
            )

        statement = (
            BankStatement.objects.all_with_archived().filter(pk=target_id).first()
        )
        if not statement:
            return Response(
                {"error": "Statement not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not statement.is_archived:
            return Response(
                {"error": "Statement is not archived"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            statement.unarchive()
            return Response(
                {"success": True, "message": "Statement restored successfully"}
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="transactions")
    def archived_transactions(self, request):
        search_query = (request.query_params.get("q") or "").strip()
        page_size = max(int(get_items_per_page(request) or 20), 1)
        page_number = request.query_params.get("page", 1)

        queryset = (
            MasterFundMonitoring.objects.all_with_archived()
            .select_related(
                "payee",
                "division",
                "fund_source",
                "nc",
                "purchase_type",
                "account_title",
                "expense_classification",
                "staff",
            )
            .filter(is_archived=True)
            .order_by("-archived_at")
        )

        if search_query:
            queryset = queryset.filter(
                Q(payee__supplier__icontains=search_query)
                | Q(particulars__icontains=search_query)
                | Q(dv_number__icontains=search_query)
                | Q(cheque_number__icontains=search_query)
                | Q(date__icontains=search_query)
            )

        total_records = queryset.count()
        total_payments_result = queryset.aggregate(total=Sum("payments"))["total"]
        total_payments = (
            float(total_payments_result) if total_payments_result is not None else 0.0
        )

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages or 1)

        page_numbers = [
            num
            for num in paginator.page_range
            if page_obj.number - 3 <= num <= page_obj.number + 3
        ]

        results = []
        for transaction in page_obj.object_list:
            results.append(
                {
                    "id": transaction.id,
                    "date": transaction.date.isoformat() if transaction.date else None,
                    "archived_at": (
                        transaction.archived_at.isoformat()
                        if transaction.archived_at
                        else None
                    ),
                    "payee": transaction.payee.supplier if transaction.payee else "",
                    "particulars": transaction.particulars or "",
                    "transaction_type": transaction.transaction_type or "",
                    "payments": float(transaction.payments or 0),
                    "cheque_status": transaction.cheque_status or "",
                    "division": (
                        str(transaction.division) if transaction.division else ""
                    ),
                    "fund_source": (
                        str(transaction.fund_source) if transaction.fund_source else ""
                    ),
                    "mooe": transaction.mooe or "",
                    "nc": str(transaction.nc) if transaction.nc else "",
                    "bank_name": "",
                    "cleared_date": (
                        transaction.cleared_date.isoformat()
                        if transaction.cleared_date
                        else None
                    ),
                    "dv_number": transaction.dv_number or "",
                    "cheque_number": transaction.cheque_number or "",
                    "account_title": (
                        str(transaction.account_title)
                        if transaction.account_title
                        else ""
                    ),
                    "expense_classification": (
                        str(transaction.expense_classification)
                        if transaction.expense_classification
                        else ""
                    ),
                    "staff": str(transaction.staff) if transaction.staff else "",
                    "tin": transaction.tin or "",
                    "tax_type": transaction.tax_type or "",
                    "purchase_type": (
                        str(transaction.purchase_type)
                        if transaction.purchase_type
                        else ""
                    ),
                    "goods_5_percent": float(transaction.goods_5_percent or 0),
                    "services_5_percent": float(transaction.services_5_percent or 0),
                    "goods_services_3_percent": float(
                        transaction.goods_services_3_percent or 0
                    ),
                    "goods_1_percent": float(transaction.goods_1_percent or 0),
                    "services_2_percent": float(transaction.services_2_percent or 0),
                    "rental_5_percent": float(transaction.rental_5_percent or 0),
                    "prof_fee_10_percent": float(transaction.prof_fee_10_percent or 0),
                }
            )

        return Response(
            {
                "search_query": search_query,
                "total_records": total_records,
                "total_payments": total_payments,
                "results": results,
                "pagination": {
                    "has_other_pages": paginator.num_pages > 1,
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(),
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "previous_page": (
                        page_obj.previous_page_number()
                        if page_obj.has_previous()
                        else None
                    ),
                    "next_page": (
                        page_obj.next_page_number() if page_obj.has_next() else None
                    ),
                    "page_numbers": page_numbers,
                },
            }
        )

    @action(
        detail=False,
        methods=["post"],
        url_path=r"transactions/(?P<transaction_id>[^/.]+)/restore",
    )
    def restore_transaction(self, request, transaction_id=None):
        try:
            target_id = int(transaction_id or 0)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid transaction id"}, status=status.HTTP_400_BAD_REQUEST
            )

        transaction = (
            MasterFundMonitoring.objects.all_with_archived()
            .filter(pk=target_id)
            .first()
        )
        if not transaction:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not transaction.is_archived:
            return Response(
                {"error": "Transaction is not archived"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction.unarchive()
            return Response(
                {"success": True, "message": "Transaction restored successfully"}
            )
        except Exception as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def _is_staff_or_superuser(self, request):
        return bool(
            request.user and (request.user.is_staff or request.user.is_superuser)
        )

    @action(detail=False, methods=["get"], url_path="form")
    def form(self, request):
        if not self._is_staff_or_superuser(request):
            return Response(
                {"detail": "Only staff members can import records."},
                status=status.HTTP_403_FORBIDDEN,
            )

        form = ImportDataForm()
        data_type_choices = [
            {"value": value, "label": label}
            for value, label in form.fields["data_type"].choices
        ]

        return Response(
            {
                "title": "Import Data",
                "subtitle": "Bulk import suppliers, bank statements, staff, or fund monitoring data from Excel/CSV files",
                "data_type": {
                    "label": form.fields["data_type"].label,
                    "choices": data_type_choices,
                },
                "file": {
                    "label": form.fields["file"].label,
                    "help_text": form.fields["file"].help_text,
                    "accept": ".xlsx,.xls,.csv",
                },
                "sheet_name": {
                    "label": form.fields["sheet_name"].label,
                    "help_text": form.fields["sheet_name"].help_text,
                    "placeholder": form.fields["sheet_name"].widget.attrs.get(
                        "placeholder", ""
                    ),
                },
                "skip_rows": {
                    "label": form.fields["skip_rows"].label,
                    "help_text": form.fields["skip_rows"].help_text,
                    "initial": (
                        form.fields["skip_rows"].initial
                        if form.fields["skip_rows"].initial is not None
                        else 0
                    ),
                },
                "skip_errors": {
                    "label": form.fields["skip_errors"].label,
                    "help_text": form.fields["skip_errors"].help_text,
                    "initial": False,
                },
            }
        )

    @action(detail=False, methods=["post"], url_path="submit")
    def submit(self, request):
        if not self._is_staff_or_superuser(request):
            return Response(
                {"detail": "Only staff members can import records."},
                status=status.HTTP_403_FORBIDDEN,
            )

        form = ImportDataForm(request.data, request.FILES)
        if not form.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": form.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_file = request.FILES.get("file")
        data_type = form.cleaned_data["data_type"]
        skip_errors = form.cleaned_data["skip_errors"]
        sheet_name = form.cleaned_data.get("sheet_name", "").strip() or None
        skip_rows = form.cleaned_data.get("skip_rows", 0) or 0

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1],
        ) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        try:
            result = process_import(
                data_type, tmp_path, skip_errors, sheet_name, skip_rows
            )

            _log_import_activity(
                request,
                uploaded_file,
                data_type,
                result,
                skip_errors,
                sheet_name,
                skip_rows,
            )

            request.session["import_result"] = result

            return Response(
                {
                    "success": True,
                    "result": result,
                    "redirect_url": "/import/result",
                }
            )
        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @action(detail=False, methods=["get"], url_path="result")
    def result(self, request):
        if not self._is_staff_or_superuser(request):
            return Response(
                {"detail": "Only staff members can access import results."},
                status=status.HTTP_403_FORBIDDEN,
            )

        result_payload = request.session.pop("import_result", None)
        if not result_payload:
            return Response(
                {"detail": "No import results found."}, status=status.HTTP_404_NOT_FOUND
            )

        summary_cards = [
            {
                "label": "Total Rows",
                "value": result_payload.get("total_rows", 0),
                "description": "Rows in file",
                "is_currency": False,
            },
            {
                "label": "Created",
                "value": result_payload.get("created", 0),
                "description": "New records added",
                "is_currency": False,
            },
            {
                "label": "Errors",
                "value": result_payload.get("errors", 0),
                "description": "Failed to import",
                "is_currency": False,
            },
        ]

        if result_payload.get("updated"):
            summary_cards.insert(
                2,
                {
                    "label": "Updated",
                    "value": result_payload.get("updated", 0),
                    "description": "Updated existing",
                    "is_currency": False,
                },
            )

        data_type = result_payload.get("data_type", "")
        view_target = {
            "Suppliers": {
                "label": "View Suppliers",
                "to": "/suppliers",
                "icon": "bi-truck",
            },
            "Bank Statements": {
                "label": "View Bank Statements",
                "to": "/bank-statements",
                "icon": "bi-building",
            },
            "Master Fund Monitoring": {
                "label": "View Master Fund Monitoring",
                "to": "/master-fund-monitoring",
                "icon": "bi-graph-up",
            },
            "Staff": {"label": "View Staff", "to": "/staff", "icon": "bi-people"},
        }.get(data_type)

        return Response(
            {
                "result": result_payload,
                "summary_cards": summary_cards,
                "view_target": view_target,
            }
        )


__all__ = [
    "ActivityLogViewSet",
    "ArchiveViewSet",
    "ImportViewSet",
    "NotificationViewSet",
]
