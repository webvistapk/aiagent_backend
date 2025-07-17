from django.db import models
from django.contrib.auth.models import User
from project.commons.common_constants import DurationType, Role

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


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10,
        choices=[(tag.value, tag.name) for tag in Role],
        default=Role.USER.value
    )

    def __str__(self):
        return f'{self.user.username} - {self.company.name} - {self.role}'