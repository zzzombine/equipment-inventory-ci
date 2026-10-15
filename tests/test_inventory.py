import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from inventory import warranty_end_date, is_serial_number_unique, save_inventory, load_inventory

class TestInventory(unittest.TestCase):

    def test_warranty_end_date(self):
        result = warranty_end_date("2026-01-15", 12)
        self.assertEqual(result, "2027-01-15")

    def test_warranty_end_date_leap_year(self):
        result = warranty_end_date("2024-01-31", 1)
        self.assertEqual(result, "2024-02-29")

    def test_serial_number_is_unique(self):
        devices = [
            {"name": "Ноутбук", "serial_number": "SN-001"},
            {"name": "Монитор", "serial_number": "SN-002"}
        ]

        result = is_serial_number_unique(devices, "SN-001")

        self.assertFalse(result)

    def test_new_serial_number_is_unique(self):
        devices = [
            {"name": "Ноутбук", "serial_number": "SN-001"},
            {"name": "Монитор", "serial_number": "SN-002"}
        ]

        result = is_serial_number_unique(devices, "SN-003")

        self.assertTrue(result)

    def test_missing_serial_number(self):
        devices = [
            {"name": "Монитор"},
            {"name": "Ноутбук", "serial_number": "SN-001"}
        ]

        result = is_serial_number_unique(devices, "SN-002")

        self.assertTrue(result)

    def test_save_inventory(self):
        devices = [
            {"name": "Ноутбук", "serial_number": "SN-001"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "inventory.json"

            with patch("inventory.DATA_FILE", temp_file):
                save_inventory(devices)

                self.assertTrue(temp_file.exists())

    def test_load_inventory(self):
        devices = [
            {"name": "Монитор", "serial_number": "SN-002"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "inventory.json"

            with patch("inventory.DATA_FILE", temp_file):
                save_inventory(devices)
                result = load_inventory()

                self.assertEqual(result, devices)

    def test_load_inventory_file_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "missing.json"

            with patch("inventory.DATA_FILE", temp_file):
                result = load_inventory()

                self.assertEqual(result, [])

    def test_save_empty_inventory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / "inventory.json"

            with patch("inventory.DATA_FILE", temp_file):
                save_inventory([])
                result = load_inventory()

                self.assertEqual(result, [])

    def test_serial_number_unique_in_empty_inventory(self):
        devices = []

        result = is_serial_number_unique(devices, "SN-001")

        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()