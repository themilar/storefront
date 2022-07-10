from django.contrib import admin
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models.aggregates import Count

from .models import Customer, CustomerProfile, User

admin.site.register(User)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "membership",
        "orders",
    ]
    # list_editable = ["customer_profile__membership"]
    list_per_page = 10
    # list_select_related = ["customerprofile"]
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))
