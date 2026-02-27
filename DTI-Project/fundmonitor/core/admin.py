from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Supplier, Staff, FundSource, ExpenseObject, Transaction

admin.site.register(Supplier)
admin.site.register(Staff)
admin.site.register(FundSource)
admin.site.register(ExpenseObject)
admin.site.register(Transaction)