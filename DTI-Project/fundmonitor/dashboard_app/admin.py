from django.contrib import admin
from .models import Staff, Supplier, FundSource, FundSourceBreakdown, BankStatement, MasterFundMonitoring, ExpenseObject, ExpenseCategory, Division, District, NegosyoCenter, BreakdownCategory

# Register your models here.

# Staff Management
admin.site.register(Staff)
admin.site.register(Division)

# Supplier Management
admin.site.register(Supplier)

# Fund Management
admin.site.register(FundSource)
admin.site.register(FundSourceBreakdown)
admin.site.register(BreakdownCategory)

# Bank Statement Management
admin.site.register(BankStatement)

# Master Fund Monitoring Management
admin.site.register(MasterFundMonitoring)

# Expense Object Management
admin.site.register(ExpenseObject)
admin.site.register(ExpenseCategory)

# Negosyo Center Management
admin.site.register(District)
admin.site.register(NegosyoCenter)
