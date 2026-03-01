from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Supplier, Staff, FundSource, Transaction

admin.site.register(Supplier)
admin.site.register(Staff)
admin.site.register(FundSource)
admin.site.register(Transaction)