"""Telegram update-терін өңдейтін негізгі логика."""

from bot import telegram
from bot.faq import FAQ_BY_ID, match
from bot.gemini import ask_gemini

WELCOME = (
    "Сәлеметсіз бе, {name}! 👋\n\n"
    "Мен — <b>ХИМИК</b> 🧪, химия бойынша көмекші ботпын.\n"
    "Химия бойынша кез келген сұрағыңызды жазыңыз — жауап беремін."
)

HELP = (
    "<b>ХИМИК — көмек</b>\n\n"
    "Сұрағыңызды жай мәтінмен жазыңыз, мысалы:\n"
    "• <i>Күкірт қышқылының молярлық массасы қанша?</i>\n"
    "• <i>Fe + O₂ → Fe₂O₃ теңдеуін теңестір</i>\n"
    "• <i>Неге темір тот басады?</i>"
)

ERROR_TEXT = "Кешіріңіз, қазір жауап бере алмадым 😔 Біраздан соң қайта көріңіз."
NON_TEXT = "Мен әзірге тек мәтіндік сұрақтарды түсінемін ✍️"


def send_faq_answer(chat_id, item):
    telegram.send_message(chat_id, item["answer"], parse_mode="HTML")


def handle_callback(callback):
    # Ескі хабарлардағы FAQ батырмалары үшін ғана қалдырылды.
    telegram.answer_callback_query(callback["id"])
    chat_id = callback["message"]["chat"]["id"]
    faq_id = callback.get("data", "").removeprefix("faq:")
    if faq_id in FAQ_BY_ID:
        send_faq_answer(chat_id, FAQ_BY_ID[faq_id])


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    if not text:
        telegram.send_message(chat_id, NON_TEXT)
        return

    # "/start@BotName" сияқты командаларды да ескереміз.
    command = text.split()[0].split("@")[0].lower() if text.startswith("/") else None

    if command == "/start":
        name = message.get("from", {}).get("first_name", "")
        name = name.replace("<", "").replace(">", "").replace("&", "")
        telegram.send_message(chat_id, WELCOME.format(name=name), parse_mode="HTML")
    elif command == "/help":
        telegram.send_message(chat_id, HELP, parse_mode="HTML")
    else:
        item = match(text)
        if item:
            send_faq_answer(chat_id, item)
            return

        telegram.send_chat_action(chat_id)
        try:
            answer = ask_gemini(text) or ERROR_TEXT
        except Exception as e:
            print(f"Gemini error: {e!r}")
            answer = ERROR_TEXT
        telegram.send_message(chat_id, answer)


def handle_update(update: dict):
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_message(update["message"])
