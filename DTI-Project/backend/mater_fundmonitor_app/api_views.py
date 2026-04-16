from rest_framework import permissions, viewsets

from .models import MasterFundMonitoring
from .serializers import MasterFundMonitoringSerializer


class MasterFundMonitoringViewSet(viewsets.ModelViewSet):
    serializer_class = MasterFundMonitoringSerializer
    permission_classes = [permissions.IsAuthenticated]
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
        )
        .all()
        .order_by("-date", "-id")
    )


__all__ = [
    "MasterFundMonitoringViewSet",
]
