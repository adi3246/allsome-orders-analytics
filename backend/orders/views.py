"""
Orders API Views

Provides REST API endpoints for:
- GET  /api/orders/          - List all orders
- GET  /api/orders/analytics/ - Get total revenue and best-selling SKU
- POST /api/orders/import/    - Upload and import a CSV file
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer
from .services import OrderService


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing orders and generating analytics."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Return total revenue and best-selling SKU as JSON."""
        analytics = OrderService.get_analytics()
        return Response(analytics)

    @action(detail=False, methods=["post"], url_path="import")
    def import_csv(self, request):
        """Import orders from an uploaded CSV file."""
        csv_file = request.FILES.get("file")

        # Validate file presence and extension
        if not csv_file:
            return Response(
                {"error": "No file provided. Upload a CSV file with key 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "File must be a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Decode, parse, validate, and import the CSV content
        try:
            content = csv_file.read().decode("utf-8")
            orders_data = OrderService.parse_csv(content)
            count = OrderService.import_orders(orders_data)
            return Response(
                {"message": f"Successfully imported {count} orders."},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            # CSV validation errors (missing columns, invalid data, etc.)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UnicodeDecodeError:
            # File encoding issues
            return Response(
                {"error": "File must be UTF-8 encoded."},
                status=status.HTTP_400_BAD_REQUEST,
            )
