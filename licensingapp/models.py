from django.db import models

class LicenseType(models.Model):
    duration = models.IntegerField()
    price_per_user = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name