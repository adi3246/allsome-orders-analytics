"""
Orders Service Layer

Contains all business logic for order processing, including:
- CSV parsing and validation
- Database import (upsert)
- Revenue calculation
- Best-selling SKU identification

This service layer is decoupled from views to promote reusability
and testability. It can be used by both API views and management commands.
"""

import csv
import io
from decimal import Decimal, InvalidOperation

from django.db.models import Sum, F

from .models import Order


class OrderService:
    """Service layer for order-related business logic."""

    @staticmethod
    def parse_csv(file_content: str) -> list[dict]:
        """
        Parse CSV content and validate each row.

        Args:
            file_content: Raw CSV string content.

        Returns:
            List of validated order dictionaries.

        Raises:
            ValueError: If CSV is empty or contains invalid data.
        """
        reader = csv.DictReader(io.StringIO(file_content))
        orders = []

        # Validate that all required CSV columns are present
        required_fields = {"order_id", "sku", "quantity", "price"}
        if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError(
                f"CSV must contain columns: {', '.join(sorted(required_fields))}"
            )

        # Parse and validate each row (start=2 accounts for header row)
        for row_num, row in enumerate(reader, start=2):
            try:
                order_id = int(row["order_id"].strip())
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Row {row_num}: Invalid order_id '{row.get('order_id')}'"
                )

            sku = row.get("sku", "").strip()
            if not sku:
                raise ValueError(f"Row {row_num}: SKU cannot be empty")

            try:
                quantity = int(row["quantity"].strip())
                if quantity < 0:
                    raise ValueError("negative")
            except (ValueError, AttributeError):
                raise ValueError(
                    f"Row {row_num}: Invalid quantity '{row.get('quantity')}'"
                )

            try:
                price = Decimal(row["price"].strip())
                if price < 0:
                    raise ValueError("negative")
            except (InvalidOperation, ValueError, AttributeError):
                raise ValueError(
                    f"Row {row_num}: Invalid price '{row.get('price')}'"
                )

            orders.append({
                "order_id": order_id,
                "sku": sku,
                "quantity": quantity,
                "price": price,
            })

        if not orders:
            raise ValueError("CSV file contains no data rows")

        return orders

    @staticmethod
    def import_orders(orders_data: list[dict]) -> int:
        """
        Import parsed order data into the database (upsert).

        Args:
            orders_data: List of validated order dictionaries.

        Returns:
            Number of orders imported.
        """
        # Use update_or_create for upsert behavior:
        # - If order_id exists, update its fields
        # - If order_id is new, create a new record
        for data in orders_data:
            Order.objects.update_or_create(
                order_id=data["order_id"],
                defaults={
                    "sku": data["sku"],
                    "quantity": data["quantity"],
                    "price": data["price"],
                },
            )
        return len(orders_data)

    @staticmethod
    def calculate_total_revenue() -> Decimal:
        """
        Calculate total revenue across all orders.

        Returns:
            Sum of (quantity * price) for all orders.
        """
        # Use Django ORM aggregation: SUM(quantity * price) across all orders
        result = Order.objects.aggregate(
            total_revenue=Sum(F("quantity") * F("price"))
        )
        # Return 0.00 if no orders exist (aggregate returns None)
        return result["total_revenue"] or Decimal("0.00")

    @staticmethod
    def find_best_selling_sku() -> dict | None:
        """
        Find the SKU with the highest total quantity sold.

        Returns:
            Dictionary with 'sku' and 'total_quantity', or None if no orders.
        """
        result = (
            Order.objects.values("sku")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")
            .first()
        )
        return result

    @classmethod
    def get_analytics(cls) -> dict:
        """
        Generate complete analytics report.

        Returns:
            Dictionary with total_revenue and best_selling_sku.
        """
        total_revenue = cls.calculate_total_revenue()
        best_selling = cls.find_best_selling_sku()

        return {
            "total_revenue": float(total_revenue),
            "best_selling_sku": best_selling,
        }
