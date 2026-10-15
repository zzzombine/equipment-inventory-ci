import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", "8005"))
MESSAGE = os.environ.get("MESSAGE", "Inventory online")
PROJECT_DIR = Path(__file__).resolve().parent
STATE_FILE = Path("/data/state.json")

def increment_counter():
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    if STATE_FILE.exists():
        with STATE_FILE.open("r", encoding="utf-8") as file:
            state = json.load(file)
    else:
        state = {"requests": 0}

    state["requests"] += 1

    temporary_file = STATE_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)

    temporary_file.replace(STATE_FILE)
    return state["requests"]

def load_devices():
    data_file = PROJECT_DIR / "inventory.json"

    if not data_file.exists():
        data_file = PROJECT_DIR / "inventory.json.example"

    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)

class InventoryHandler(BaseHTTPRequestHandler):
    def send_json(self, status_code, data):
        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        # Автоматические проверки не увеличивают счётчик.
        if path == "/health":
            self.send_json(200, {"status": "ok"})
            return

        try:
            requests_count = increment_counter()
        except (OSError, ValueError, KeyError, TypeError):
            self.log_error("Не удалось обновить счётчик запросов")
            self.send_json(500, {"error": "Ошибка сохранения счётчика"})
            return

        if path == "/inventory":
            try:
                devices = load_devices()
            except (OSError, ValueError):
                self.send_json(
                    500,
                    {"error": "Не удалось прочитать список оборудования"},
                )
                return

            self.send_json(
                200,
                {
                    "message": MESSAGE,
                    "service_version": "1.1",
                    "hostname": socket.gethostname(),
                    "requests": requests_count,
                    "devices": devices,
                },
            )
        else:
            self.send_json(404, {"error": "Маршрут не найден"})

def main():
    server = HTTPServer(("0.0.0.0", PORT), InventoryHandler)
    print(f"Сервис запущен на порту {PORT}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервис остановлен", flush=True)
    finally:
        server.server_close()

if __name__ == "__main__":
    main()