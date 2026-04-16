from rest_framework import viewsets

from user_app.permissions import IsAuthenticatedReadOnlyOrStaff

from .models import MasterFundMonitoring
from .serializers import MasterFundMonitoringSerializer


class MasterFundMonitoringViewSet(viewsets.ModelViewSet):
    serializer_class = MasterFundMonitoringSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]
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
