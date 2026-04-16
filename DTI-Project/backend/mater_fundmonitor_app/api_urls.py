from rest_framework.routers import DefaultRouter

from .api_views import MasterFundMonitoringViewSet

router = DefaultRouter()
router.include_format_suffixes = False
router.register(
    "master-fund-monitoring",
    MasterFundMonitoringViewSet,
    basename="mater-fundmonitor-master-fund-monitoring",
)

urlpatterns = router.urls
