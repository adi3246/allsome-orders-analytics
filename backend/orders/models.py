"""
Orders Models

Defines the database schema for order data imported from CSV files.
Each order represents a single line item with SKU, quantity, and price.
"""

from django.db import models


class Order(models.Model):
    """Represents a single order line item."""

    # Unique identifier from the CSV (not the auto-generated PK)
    order_id = models.IntegerField(unique=True)
    # Stock Keeping Unit - product identifier (e.g., SKU-A123)
    sku = models.CharField(max_length=50)
    # Number of units ordered (must be non-negative)
    quantity = models.PositiveIntegerField()
    # Unit price per item in the order
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["order_id"]

    def __str__(self):
        return f"Order {self.order_id} - {self.sku}"

    @property
    def line_total(self):
        """Calculate revenue for this order line (quantity * price)."""
        return self.quantity * self.price
