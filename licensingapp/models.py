from django.db import models
from project.commons.common_constants import DurationType

class LicenseType(models.Model):
    duration = models.IntegerField()
    duration_type = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in DurationType],
        default=DurationType.MONTHS.value
    )
    price_per_user = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name