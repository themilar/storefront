from django.contrib import admin
from . import models

admin.site.register([models.Cart, models.Collection,
                     models.Customer, models.Product])
