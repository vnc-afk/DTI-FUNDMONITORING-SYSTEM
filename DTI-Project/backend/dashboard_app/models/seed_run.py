from django.db import models


class SeedRun(models.Model):
    key = models.CharField(max_length=100, unique=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-executed_at"]
        verbose_name = "Seed Run"
        verbose_name_plural = "Seed Runs"

    def __str__(self):
        return f"{self.key} @ {self.executed_at:%Y-%m-%d %H:%M:%S}"
