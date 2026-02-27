from django.contrib import admin
from .models import Staff, Supplier, FundSource, BudgetBreakdown, BankStatement, MasterFundMonitoring

# Register your models here.

# Staff Management
admin.site.register(Staff)

# Supplier Management
admin.site.register(Supplier)

# Fund Management
admin.site.register(FundSource)
admin.site.register(BudgetBreakdown)

# Bank Statement Management
admin.site.register(BankStatement)

# Master Fund Monitoring Management
admin.site.register(MasterFundMonitoring)
