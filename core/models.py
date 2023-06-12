from email.policy import default

from django.db import models


class Rate(models.Model):
    target = models.TextField(blank=False)
    base = models.TextField(blank=False)
    rate = models.FloatField(blank=False)
    date = models.DateField(blank=False)

    class Meta:
        unique_together = (
            "base",
            "target",
        )
