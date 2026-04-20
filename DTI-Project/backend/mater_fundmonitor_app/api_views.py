from django.db.models import Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from user_app.permissions import IsAuthenticatedReadOnlyOrStaff

from .models import MasterFundMonitoring
from .serializers import MasterFundMonitoringSerializer


class MasterFundMonitoringViewSet(viewsets.ModelViewSet):
    from rest_framework import filters
    from user_app.pagination import UserPreferencePageNumberPagination

    serializer_class = MasterFundMonitoringSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]
    pagination_class = UserPreferencePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "payee__supplier",
        "particulars",
        "cheque_number",
        "dv_number",
        "fund_source__name",
        "division__name",
        "nc__name",
        "account_title__name",
        "expense_classification__name",
        "staff__first_name",
        "staff__last_name",
        "mooe",
    ]

    def get_queryset(self):
        queryset = (
            MasterFundMonitoring.objects.select_related(
                "division",
                "fund_source",
                "nc",
                "payee",
                "purchase_type",
                "account_title",
                "expense_classification",
                "staff",
                "cancelled_by",
            )
            .all()
            .order_by("-date", "-id")
        )

        if self.action != "list":
            return queryset

        include_cancelled = (
            (self.request.query_params.get("include_cancelled") or "")
            .strip()
            .lower()
            in {"1", "true", "yes", "y"}
        )

        if not include_cancelled:
            queryset = queryset.filter(is_cancelled=False)

        cheque_status = (self.request.query_params.get("cheque_status") or "").strip()
        if cheque_status:
            if cheque_status == "Cancelled":
                queryset = queryset.filter(is_cancelled=True)
            elif cheque_status == "Pending":
                queryset = queryset.filter(
                    is_cancelled=False
                ).filter(Q(cheque_status="Pending") | Q(cheque_status__isnull=True) | Q(cheque_status=""))
            else:
                queryset = queryset.filter(cheque_status=cheque_status)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        totals = queryset.aggregate(
            total_payments=Sum("payments"),
            total_downloads=Sum("downloads"),
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["total_payments"] = totals["total_payments"] or 0
            response.data["total_downloads"] = totals["total_downloads"] or 0
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "results": serializer.data,
                "count": len(serializer.data),
                "total_payments": totals["total_payments"] or 0,
                "total_downloads": totals["total_downloads"] or 0,
            },
            status=status.HTTP_200_OK,
        )

    def _ensure_editable(self, instance):
        if instance.is_cancelled:
            raise ValidationError(
                {"detail": "Cancelled records cannot be edited. Uncancel the record first."}
            )

    def update(self, request, *args, **kwargs):
        self._ensure_editable(self.get_object())
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._ensure_editable(self.get_object())
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        instance = self.get_object()
        reason = (request.data.get("reason") or "").strip()
        instance.cancel(
            user=request.user if request.user.is_authenticated else None,
            reason=reason,
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def uncancel(self, request, pk=None):
        instance = self.get_object()
        instance.uncancel()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = [
    "MasterFundMonitoringViewSet",
]
