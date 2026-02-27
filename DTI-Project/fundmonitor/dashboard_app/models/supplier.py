from django.db import models


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
