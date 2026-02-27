from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    tin_number = models.CharField(max_length=50)
    philgeps_registration = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    propprietor = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FundSource(models.Model):
    name = models.CharField(max_length=100)
    annual_budget = models.DecimalField(max_digits=15, decimal_places=2)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.year})"


class ExpenseObject(models.Model):
    code = models.CharField(max_length=50)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.description}"


class Transaction(models.Model):
    division = models.CharField(max_length=100)

    fund_source = models.ForeignKey(FundSource, on_delete=models.CASCADE)
    expense_object = models.ForeignKey(ExpenseObject, on_delete=models.SET_NULL, null=True)

    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateField()
    payee = models.CharField(max_length=255)
    particulars = models.TextField()

    dv_number = models.CharField(max_length=100, blank=True, null=True)
    cheque_number = models.CharField(max_length=100, blank=True, null=True)
    cleared_date = models.DateField(blank=True, null=True)

    downloads_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    cheque_status = models.CharField(max_length=50, blank=True, null=True)
    purchase_type = models.CharField(max_length=100, blank=True, null=True)
    tax_type = models.CharField(max_length=100, blank=True, null=True)

    encoded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payee} - {self.payment_amount}"