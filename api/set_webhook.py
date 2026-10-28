"""Webhook-ты бір рет тіркеу: /api/set_webhook?secret=<TELEGRAM_SECRET_TOKEN>"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import telegram  # noqa: E402

COMMANDS = [
    {"command": "start", "description": "Басынан бастау"},
    {"command": "faq", "description": "Жиі қойылатын сұрақтар"},
    {"command": "help", "description": "Көмек"},
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        secret = os.environ.get("TELEGRAM_SECRET_TOKEN", "")
        query = parse_qs(urlparse(self.path).query)

        if not secret or query.get("secret", [""])[0] != secret:
            result, status = {"ok": False, "error": "wrong or missing secret"}, 403
        else:
            webhook_url = f"https://{self.headers.get('Host')}/api/webhook"
            result = {
                "webhook_url": webhook_url,
                "setWebhook": telegram.call(
                    "setWebhook",
                    url=webhook_url,
                    secret_token=secret,
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True,
                ),
                "setMyCommands": telegram.call("setMyCommands", commands=COMMANDS),
            }
            status = 200

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
