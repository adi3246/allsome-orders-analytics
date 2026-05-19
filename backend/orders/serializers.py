from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model."""

    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = ["id", "order_id", "sku", "quantity", "price", "line_total"]


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for the analytics response."""

    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    best_selling_sku = serializers.DictField()
