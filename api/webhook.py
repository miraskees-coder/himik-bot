"""Vercel serverless функциясы: Telegram webhook қабылдайды."""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.handlers import handle_update  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _reply(self, status: int, body: str):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        self._reply(200, "ХИМИК бот жұмыс істеп тұр 🧪")

    def do_POST(self):
        secret = os.environ.get("TELEGRAM_SECRET_TOKEN")
        if secret and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
            self._reply(403, "forbidden")
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            update = json.loads(self.rfile.read(length) or b"{}")
            handle_update(update)
        except Exception as e:
            # Telegram қайта-қайта жібермеуі үшін әрқашан 200 қайтарамыз.
            print(f"Update handling error: {e!r}")

        self._reply(200, "ok")
