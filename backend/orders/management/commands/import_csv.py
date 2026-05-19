"""
Management Command: import_csv

Usage:
    python manage.py import_csv <csv_path> [--output <json_path>]

This command reads an orders CSV file, imports it into the database,
calculates analytics (total revenue and best-selling SKU), and
optionally saves the result to a JSON file.
"""

import json
import sys

from django.core.management.base import BaseCommand, CommandError

from orders.services import OrderService


class Command(BaseCommand):
    """Management command to import orders from a CSV file and output analytics."""

    help = "Import orders from a CSV file and display analytics as JSON"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Path to save the JSON output (optional)",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        # Step 1: Read the CSV file from disk
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")
        except IOError as e:
            raise CommandError(f"Error reading file: {e}")

        # Step 2: Parse and validate CSV content
        try:
            orders_data = OrderService.parse_csv(content)
        except ValueError as e:
            raise CommandError(f"CSV validation error: {e}")

        # Step 3: Import orders into the database
        count = OrderService.import_orders(orders_data)
        self.stdout.write(self.style.SUCCESS(f"Imported {count} orders."))

        # Step 4: Calculate and display analytics
        analytics = OrderService.get_analytics()
        output_json = json.dumps(analytics, indent=2)

        self.stdout.write("\nAnalytics Result:")
        self.stdout.write(output_json)

        # Step 5: Optionally save output to a JSON file
        output_path = options.get("output")
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_json)
            self.stdout.write(self.style.SUCCESS(f"\nOutput saved to: {output_path}"))
