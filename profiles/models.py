from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class User(AbstractUser):
    class Types(models.TextChoices):
        BASE = "BASE", "Base"
        CUSTOMER = "CUSTOMER", "Customer"
        INVENTOR = "INVENTOR", "Inventor"

    # Ensures that creating new users through proxy models works
    base_type = Types.BASE
    # What type of user are we?
    type = models.CharField(
        _("Type"), max_length=50, choices=Types.choices, default=Types.BASE
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.type = self.base_type
        return super().save(*args, **kwargs)


class CustomerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(type=User.Types.CUSTOMER)


class Customer(User):
    base_type = User.Types.CUSTOMER
    objects = CustomerManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        proxy = True
        ordering = ["first_name", "last_name"]

    @property
    def extra(self):
        return self.customerprofile

    def membership(self):
        return self.customerprofile.membership


class CustomerProfile(models.Model):
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)

    class Membership(models.TextChoices):
        BRONZE = "B", _("Bronze")
        SILVER = "S", _("Silver")
        GOLD = "G", _("Gold")

    membership = models.CharField(
        max_length=1, choices=Membership.choices, default=Membership.BRONZE
    )
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
