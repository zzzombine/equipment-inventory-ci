import json
import calendar

from pathlib import Path
from datetime import date

DATA_FILE = Path("inventory.json")
WARRANTY_MONTHS = 12 # Значение по умолчанию


def warranty_end_date(purchase_date, months=WARRANTY_MONTHS):
    purchase = date.fromisoformat(purchase_date)
    month_index = purchase.month - 1 + months
    year = purchase.year + month_index // 12
    month = month_index % 12 + 1
    day = min(purchase.day, calendar.monthrange(year, month)[1])
    return date(year, month, day).isoformat()

def load_inventory():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_inventory(devices):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(devices, file, ensure_ascii=False, indent=2)

def is_serial_number_unique(devices, serial_number):
    return True

def main():
    devices = load_inventory()

    while True:
        print("\n1 - Показать устройства")
        print("2 - Добавить устройство")
        print("3 - Найти устройство")
        print("0 - Выход")
        choice = input("Выберите действие: ")

        if choice == "1":
            print(f"\nУстройств в учёте: {len(devices)}")

            for device in devices:
                print(
                    f"— {device['name']}"
                    f"(Серийный номер: {device.get('serial_number', 'не указан')})"
                )
                if "purchase_date" in device:
                    print("Гарантия до: " + warranty_end_date(device["purchase_date"], device.get("warranty_months", WARRANTY_MONTHS)))
        elif choice == "2":
            name = input("Название устройства: ").strip()
            if not name:
                print("Название не может быть пустым")
                continue

            serial_number = input("Серийный номер: ").strip()
            if not serial_number:
                print("Серийный номер не должен быть пустым")
                continue

            if not is_serial_number_unique(devices, serial_number):
                print("Устройство с таким серийным номером уже существует")
                continue

            purchase_date = input("Дата покупки (ГГГГ-ММ-ДД): ").strip()
            try:
                date.fromisoformat(purchase_date)
            except ValueError:
                print("Неверный формат даты")
                continue

            months_input = input(f"Срок гарантии в месяцах (Enter - {WARRANTY_MONTHS}): ").strip()
            try:
                warranty_months = (
                    int(months_input)
                    if months_input
                    else WARRANTY_MONTHS
                )
                if warranty_months <= 0:
                    raise ValueError
            except:
                print("Срок гарантии должен быть положительным целым числом")
                continue

            devices.append({
                "name": name,
                "serial_number": serial_number,
                "purchase_date": purchase_date,
                "warranty_months": warranty_months,
            })
            save_inventory(devices)
            print(f"Устройство '{name}' добавлено")
        elif choice == "3":
            query = input("Название или серийный номер: ").strip().lower()
            found = [
                device for device in devices
                if query in device["name"].lower()
                or query in device.get("serial_number", "").lower()
            ]

            if found:
                for device in found:
                    print(
                        f"— {device['name']} "
                        f"(Серийный номер: {device.get('serial_number', 'не указан')})"
                    )
            else:
                print("Устройства не найдены")
        elif choice == "0":
            break
        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()