from django.contrib import admin
from .models import *

admin.site.register(LicenseType)
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(CompanyLicense)