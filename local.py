"""Ботты ноутбукте тексеру (polling режимі): python local.py

Vercel-де бұл файл қолданылмайды. Кілттер .env файлынан оқылады.
"""

import os
import time

import requests

try:
    # Windows сертификаттарын қолдану (антивирус/прокси SSL тексеретін жағдайда керек).
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass


def load_env(path=".env"):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


load_env()

from bot import telegram  # noqa: E402
from bot.handlers import handle_update  # noqa: E402


def main():
    # Webhook орнатылып тұрса, getUpdates жұмыс істемейді — уақытша өшіреміз.
    telegram.call("deleteWebhook")
    me = telegram.call("getMe")
    print(f"✅ @{me['result']['username']} іске қосылды. Тоқтату: Ctrl+C")

    offset = None
    while True:
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/getUpdates",
                params={"timeout": 30, "offset": offset},
                timeout=40,
            ).json()
        except requests.RequestException as e:
            print(f"Желі қатесі: {e!r}")
            time.sleep(3)
            continue

        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            text = update.get("message", {}).get("text") or update.get("callback_query", {}).get("data")
            print(f"← {text}")
            try:
                handle_update(update)
            except Exception as e:
                print(f"Қате: {e!r}")


if __name__ == "__main__":
    main()
