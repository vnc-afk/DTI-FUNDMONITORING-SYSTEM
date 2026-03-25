from django.contrib import admin

from data_management_app.models import (
	BreakdownCategory,
	District,
	Division,
	ExpenseCategory,
	ExpenseObject,
	FundSource,
	FundSourceBreakdown,
	NegosyoCenter,
	PurchaseType,
	Staff,
	Supplier,
	TaxTable,
)

admin.site.register(Staff)
admin.site.register(Division)
admin.site.register(Supplier)
admin.site.register(FundSource)
admin.site.register(FundSourceBreakdown)
admin.site.register(BreakdownCategory)
admin.site.register(ExpenseObject)
admin.site.register(ExpenseCategory)
admin.site.register(District)
admin.site.register(NegosyoCenter)
admin.site.register(PurchaseType)
admin.site.register(TaxTable)
