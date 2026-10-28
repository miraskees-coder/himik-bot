"""Telegram Bot API-ға қарапайым HTTP шақырулар."""

import os

import requests

API_URL = "https://api.telegram.org/bot{token}/{method}"
MAX_MESSAGE_LENGTH = 4096


def call(method: str, **params):
    url = API_URL.format(token=os.environ["TELEGRAM_BOT_TOKEN"], method=method)
    resp = requests.post(url, json=params, timeout=15)
    data = resp.json()
    if not data.get("ok"):
        print(f"Telegram API error in {method}: {data}")
    return data


def send_message(chat_id, text: str, parse_mode=None, reply_markup=None):
    # Telegram бір хабарда 4096 символдан артық қабылдамайды.
    chunks = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    for i, chunk in enumerate(chunks):
        params = {"chat_id": chat_id, "text": chunk}
        if parse_mode:
            params["parse_mode"] = parse_mode
        if reply_markup and i == len(chunks) - 1:
            params["reply_markup"] = reply_markup
        call("sendMessage", **params)


def send_chat_action(chat_id, action: str = "typing"):
    call("sendChatAction", chat_id=chat_id, action=action)


def answer_callback_query(callback_query_id: str, text=None):
    params = {"callback_query_id": callback_query_id}
    if text:
        params["text"] = text
    call("answerCallbackQuery", **params)
