from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from user_app.permissions import IsAuthenticatedReadOnlyOrStaff

from .models import MasterFundMonitoring
from .serializers import MasterFundMonitoringSerializer


class MasterFundMonitoringViewSet(viewsets.ModelViewSet):
    serializer_class = MasterFundMonitoringSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

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
            queryset = queryset.filter(cheque_status=cheque_status)

        return queryset

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
