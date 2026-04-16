from rest_framework.routers import DefaultRouter

from .api_views import (
    ActivityLogViewSet,
    ArchiveViewSet,
    ImportViewSet,
    NotificationViewSet,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register("activity-logs", ActivityLogViewSet, basename="dashboard-activity-log")
router.register("archive", ArchiveViewSet, basename="dashboard-archive")
router.register("import", ImportViewSet, basename="dashboard-import")
router.register("notifications", NotificationViewSet, basename="dashboard-notification")

urlpatterns = router.urls
