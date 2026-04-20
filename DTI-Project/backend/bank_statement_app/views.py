from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user_app.permissions import (
    IsAuthenticatedReadOnlyOrStaff,
    IsStaffOrSuperuser,
)
from user_app.utils import get_items_per_page

from .forms import BankStatementForm
from .models import BankStatement
from .serializers import BankStatementSerializer


class BankStatementListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        status_filter = (request.query_params.get("status") or "").strip()
        try:
            page_size = int(request.query_params.get("page_size") or get_items_per_page(request))
        except (TypeError, ValueError):
            page_size = get_items_per_page(request)
        page_size = max(page_size, 1)

        statements_qs = BankStatement.objects.all().order_by("-date", "-created_at")

        if query:
            statements_qs = statements_qs.filter(
                Q(description__icontains=query) | Q(check_number__icontains=query)
            )

        if status_filter in {"Cleared", "On Process"}:
            statements_qs = statements_qs.filter(status=status_filter)

        statement_count = statements_qs.count()
        totals = statements_qs.aggregate(
            total_debits=Sum("debit"), total_credits=Sum("credit")
        )

        total_debits = totals["total_debits"] or 0
        total_credits = totals["total_credits"] or 0

        latest_statement = (
            BankStatement.objects.all().order_by("-date", "-created_at").first()
        )
        current_debit = (
            latest_statement.debit if latest_statement and latest_statement.debit else 0
        )
        current_credit = (
            latest_statement.credit
            if latest_statement and latest_statement.credit
            else 0
        )
        current_balance = (
            latest_statement.balance
            if latest_statement and latest_statement.balance
            else 0
        )

        paginator = Paginator(statements_qs, page_size)
        page_obj = paginator.get_page(request.query_params.get("page"))

        serializer = BankStatementSerializer(page_obj.object_list, many=True)

        response_payload = {
            "statements": serializer.data,
            "pagination": {
                "page": page_obj.number,
                "pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "count": paginator.count,
                "page_size": page_obj.paginator.per_page,
            },
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
                {
                    "title": "Current Debit",
                    "value": current_debit,
                    "icon": "arrow-down",
                    "description": "Most recent debit",
                    "css_class": "text-danger",
                },
                {
                    "title": "Current Credit",
                    "value": current_credit,
                    "icon": "arrow-up",
                    "description": "Most recent credit",
                    "css_class": "text-success",
                },
                {
                    "title": "Current Balance",
                    "value": current_balance,
                    "icon": "wallet",
                    "description": "Latest running balance",
                    "css_class": "text-primary",
                },
            ],
        }
        return Response(response_payload, status=status.HTTP_200_OK)

    def post(self, request):
        is_first_transaction = not BankStatement.objects.exists()
        form = BankStatementForm(
            request.data, is_first_transaction=is_first_transaction
        )
        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        statement = form.save()
        serializer = BankStatementSerializer(statement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BankStatementDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

    def get(self, request, pk):
        statement = get_object_or_404(BankStatement, pk=pk)
        serializer = BankStatementSerializer(statement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        statement = get_object_or_404(BankStatement, pk=pk)
        form = BankStatementForm(
            request.data, instance=statement, is_first_transaction=False
        )
        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        updated_statement = form.save()
        serializer = BankStatementSerializer(updated_statement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        statement = get_object_or_404(BankStatement, pk=pk)

        merged_data = {
            "date": statement.date,
            "description": statement.description,
            "check_number": statement.check_number,
            "debit": statement.debit,
            "credit": statement.credit,
            "balance": statement.balance,
            "status": statement.status,
        }
        merged_data.update(request.data)

        form = BankStatementForm(
            merged_data, instance=statement, is_first_transaction=False
        )
        if not form.is_valid():
            return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)

        updated_statement = form.save()
        serializer = BankStatementSerializer(updated_statement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        statement = get_object_or_404(BankStatement, pk=pk)
        statement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BankStatementStatusUpdateAPIView(APIView):
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request, pk):
        statement = get_object_or_404(BankStatement, pk=pk)
        statement_status = request.data.get("status")
        if statement_status not in {"Cleared", "On Process"}:
            return Response(
                {"success": False, "message": "Invalid status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        statement.status = statement_status
        statement.save(update_fields=["status", "updated_at"])
        return Response({"success": True}, status=status.HTTP_200_OK)


class BankStatementBulkDeleteAPIView(APIView):
    permission_classes = [IsStaffOrSuperuser]

    def post(self, request):
        ids = request.data.get("ids") or []
        if not isinstance(ids, list):
            return Response(
                {"success": False, "message": "Invalid payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = BankStatement.objects.filter(id__in=ids).delete()
        return Response(
            {"success": True, "deleted_count": deleted_count}, status=status.HTTP_200_OK
        )


__all__ = [
    "BankStatementListCreateAPIView",
    "BankStatementDetailAPIView",
    "BankStatementStatusUpdateAPIView",
    "BankStatementBulkDeleteAPIView",
]
