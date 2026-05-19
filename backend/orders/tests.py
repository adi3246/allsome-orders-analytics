from decimal import Decimal
from io import StringIO

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Order
from .services import OrderService


class OrderModelTest(TestCase):
    """Tests for the Order model."""

    def test_line_total(self):
        order = Order(order_id=1, sku="SKU-A", quantity=3, price=Decimal("10.00"))
        self.assertEqual(order.line_total, Decimal("30.00"))

    def test_str_representation(self):
        order = Order(order_id=1, sku="SKU-A", quantity=1, price=Decimal("5.00"))
        self.assertEqual(str(order), "Order 1 - SKU-A")


class OrderServiceParseCSVTest(TestCase):
    """Tests for CSV parsing logic."""

    def test_valid_csv(self):
        content = "order_id,sku,quantity,price\n1001,SKU-A,2,50.0\n1002,SKU-B,1,100.0"
        result = OrderService.parse_csv(content)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["order_id"], 1001)
        self.assertEqual(result[0]["sku"], "SKU-A")
        self.assertEqual(result[0]["quantity"], 2)
        self.assertEqual(result[0]["price"], Decimal("50.0"))

    def test_missing_columns(self):
        content = "order_id,sku\n1001,SKU-A"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("CSV must contain columns", str(ctx.exception))

    def test_invalid_order_id(self):
        content = "order_id,sku,quantity,price\nabc,SKU-A,2,50.0"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("Invalid order_id", str(ctx.exception))

    def test_empty_sku(self):
        content = "order_id,sku,quantity,price\n1001,,2,50.0"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("SKU cannot be empty", str(ctx.exception))

    def test_negative_quantity(self):
        content = "order_id,sku,quantity,price\n1001,SKU-A,-1,50.0"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("Invalid quantity", str(ctx.exception))

    def test_invalid_price(self):
        content = "order_id,sku,quantity,price\n1001,SKU-A,2,abc"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("Invalid price", str(ctx.exception))

    def test_empty_csv(self):
        content = "order_id,sku,quantity,price\n"
        with self.assertRaises(ValueError) as ctx:
            OrderService.parse_csv(content)
        self.assertIn("no data rows", str(ctx.exception))


class OrderServiceAnalyticsTest(TestCase):
    """Tests for analytics calculations."""

    def setUp(self):
        Order.objects.create(order_id=1001, sku="SKU-A123", quantity=2, price=Decimal("50.0"))
        Order.objects.create(order_id=1002, sku="SKU-B456", quantity=1, price=Decimal("120.0"))
        Order.objects.create(order_id=1003, sku="SKU-A123", quantity=3, price=Decimal("50.0"))
        Order.objects.create(order_id=1004, sku="SKU-C789", quantity=5, price=Decimal("20.0"))
        Order.objects.create(order_id=1005, sku="SKU-B456", quantity=2, price=Decimal("120.0"))

    def test_total_revenue(self):
        revenue = OrderService.calculate_total_revenue()
        # (2*50) + (1*120) + (3*50) + (5*20) + (2*120) = 100+120+150+100+240 = 710
        self.assertEqual(revenue, Decimal("710"))

    def test_best_selling_sku(self):
        result = OrderService.find_best_selling_sku()
        self.assertEqual(result["sku"], "SKU-A123")
        self.assertEqual(result["total_quantity"], 5)

    def test_analytics_output(self):
        analytics = OrderService.get_analytics()
        self.assertEqual(analytics["total_revenue"], 710.0)
        self.assertEqual(analytics["best_selling_sku"]["sku"], "SKU-A123")
        self.assertEqual(analytics["best_selling_sku"]["total_quantity"], 5)

    def test_empty_database(self):
        Order.objects.all().delete()
        revenue = OrderService.calculate_total_revenue()
        self.assertEqual(revenue, Decimal("0.00"))
        best = OrderService.find_best_selling_sku()
        self.assertIsNone(best)


class OrderAPITest(APITestCase):
    """Tests for the REST API endpoints."""

    def setUp(self):
        Order.objects.create(order_id=1001, sku="SKU-A123", quantity=2, price=Decimal("50.0"))
        Order.objects.create(order_id=1002, sku="SKU-B456", quantity=1, price=Decimal("120.0"))

    def test_list_orders(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_analytics_endpoint(self):
        response = self.client.get("/api/orders/analytics/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_revenue", response.data)
        self.assertIn("best_selling_sku", response.data)

    def test_import_no_file(self):
        response = self.client.post("/api/orders/import/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_valid_csv(self):
        csv_content = "order_id,sku,quantity,price\n2001,SKU-X,4,30.0"
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_file = SimpleUploadedFile("test.csv", csv_content.encode(), content_type="text/csv")
        response = self.client.post("/api/orders/import/", {"file": csv_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(order_id=2001).exists())
