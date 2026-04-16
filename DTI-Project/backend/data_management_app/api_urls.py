from rest_framework.routers import DefaultRouter

from .api_views import (
    BreakdownCategoryViewSet,
    DistrictViewSet,
    DivisionViewSet,
    ExpenseCategoryViewSet,
    ExpenseObjectViewSet,
    FundSourceBreakdownViewSet,
    FundSourceViewSet,
    NegosyoCenterViewSet,
    PurchaseTypeViewSet,
    StaffViewSet,
    SupplierViewSet,
    TaxTableViewSet,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register("divisions", DivisionViewSet, basename="data-management-division")
router.register("staff", StaffViewSet, basename="data-management-staff")
router.register("suppliers", SupplierViewSet, basename="data-management-supplier")
router.register(
    "fund-sources", FundSourceViewSet, basename="data-management-fund-source"
)
router.register(
    "breakdown-categories",
    BreakdownCategoryViewSet,
    basename="data-management-breakdown-category",
)
router.register(
    "fund-source-breakdowns",
    FundSourceBreakdownViewSet,
    basename="data-management-fund-source-breakdown",
)
router.register(
    "expense-objects", ExpenseObjectViewSet, basename="data-management-expense-object"
)
router.register(
    "expense-categories",
    ExpenseCategoryViewSet,
    basename="data-management-expense-category",
)
router.register("districts", DistrictViewSet, basename="data-management-district")
router.register(
    "negosyo-centers", NegosyoCenterViewSet, basename="data-management-negosyo-center"
)
router.register(
    "purchase-types", PurchaseTypeViewSet, basename="data-management-purchase-type"
)
router.register("tax-table", TaxTableViewSet, basename="data-management-tax-table")

urlpatterns = router.urls
