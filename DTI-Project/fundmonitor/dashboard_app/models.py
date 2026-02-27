from django.db import models

# Create your models here.

class Staff(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, blank=True)
    last_name = models.CharField(max_length=100)
    division = models.CharField(max_length=100)

    def __str__(self):
        middle = f" {self.middle_initial}" if self.middle_initial else ""
        return f"{self.first_name}{middle} {self.last_name}"
    

class Supplier(models.Model):

    CATEGORY_CHOICES = [
        ('NV', 'NV'),
        ('V', 'V'),
    ]
    supplier = models.CharField(max_length=200)
    tin = models.CharField(max_length=50)
    vat_status = models.CharField(max_length=2, choices=CATEGORY_CHOICES) 
    philgeps_registration = models.CharField(max_length=100)
    address = models.TextField()
    propprietor = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.supplier

class FundSource(models.Model):
    name = models.CharField(max_length=100)
    annual_budget = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.name


class BudgetBreakdown(models.Model):
    fund_source = models.ForeignKey(FundSource, on_delete=models.CASCADE, related_name='breakdowns')
    category = models.CharField(max_length=50)
    budget = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.fund_source.name} - {self.category}"


class BankStatement(models.Model):

    CATEGORY_CHOICES = [
        ('Cleared', 'Cleared'),
        ('On Process', 'On Process'),
    ]
    date = models.DateField()
    description = models.CharField(max_length=255)
    check_number = models.CharField(max_length=50, blank=True, default='')
    debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.description