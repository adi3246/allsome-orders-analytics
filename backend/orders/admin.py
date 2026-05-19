from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "sku", "quantity", "price", "line_total"]
    search_fields = ["sku", "order_id"]
    list_filter = ["sku"]
