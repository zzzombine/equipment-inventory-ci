
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Путь к развёрнутому приложению
deploy_dir = Path("deploy/test").resolve()
sys.path.insert(0, str(deploy_dir))

import inventory


def smoke_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "inventory.json"

        with patch.object(inventory, "DATA_FILE", temp_file):
            devices = inventory.load_inventory()

            new_device = {
                "name": "Тестовый ноутбук",
                "serial_number": "TEST-001",
                "purchase_date": "2026-10-15",
                "warranty_months": 12
            }

            assert inventory.is_serial_number_unique(
                devices, new_device["serial_number"]
            ), "Серийный номер уже занят"

            devices.append(new_device)
            inventory.save_inventory(devices)

            saved_devices = inventory.load_inventory()

            assert new_device in saved_devices, (
                "Устройство не сохранилось"
            )

            print("SMOKE TEST PASSED")


if __name__ == "__main__":
    smoke_test()
