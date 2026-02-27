from django.db import models


class Staff(models.Model):
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=5, blank=True)
    last_name = models.CharField(max_length=100)
    division = models.CharField(max_length=100)

    def __str__(self):
        middle = f" {self.middle_initial}" if self.middle_initial else ""
        return f"{self.first_name}{middle} {self.last_name}"
