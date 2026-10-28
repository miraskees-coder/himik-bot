"""Telegram update-терін өңдейтін негізгі логика."""

from bot import telegram
from bot.faq import FAQ, FAQ_BY_ID, match
from bot.gemini import ask_gemini

WELCOME = (
    "Сәлеметсіз бе, {name}! 👋\n\n"
    "Мен — <b>ХИМИК</b> 🧪, химия бойынша көмекші ботпын.\n\n"
    "• Төмендегі батырмалардан жиі қойылатын сұрақты таңдаңыз\n"
    "• Немесе кез келген химиялық сұрағыңызды жай жазып жіберіңіз\n\n"
    "Командалар: /faq — сұрақтар тізімі, /help — көмек"
)

HELP = (
    "<b>ХИМИК — көмек</b>\n\n"
    "/start — басынан бастау\n"
    "/faq — жиі қойылатын сұрақтар\n"
    "/help — осы хабар\n\n"
    "Сұрағыңызды жай мәтінмен жазыңыз, мысалы:\n"
    "• <i>Күкірт қышқылының молярлық массасы қанша?</i>\n"
    "• <i>Fe + O₂ → Fe₂O₃ теңдеуін теңестір</i>\n"
    "• <i>Неге темір тот басады?</i>"
)

ERROR_TEXT = "Кешіріңіз, қазір жауап бере алмадым 😔 Біраздан соң қайта көріңіз."
NON_TEXT = "Мен әзірге тек мәтіндік сұрақтарды түсінемін ✍️"


def faq_keyboard():
    return {
        "inline_keyboard": [
            [{"text": item["question"], "callback_data": f"faq:{item['id']}"}]
            for item in FAQ
        ]
    }


def back_keyboard():
    return {"inline_keyboard": [[{"text": "📋 Барлық сұрақтар", "callback_data": "faq:list"}]]}


def send_faq_answer(chat_id, item):
    text = f"<b>❓ {item['question']}</b>\n\n{item['answer']}"
    telegram.send_message(chat_id, text, parse_mode="HTML", reply_markup=back_keyboard())


def send_faq_list(chat_id):
    telegram.send_message(
        chat_id,
        "📋 <b>Жиі қойылатын сұрақтар</b>\n\nСұрақты таңдаңыз:",
        parse_mode="HTML",
        reply_markup=faq_keyboard(),
    )


def handle_callback(callback):
    telegram.answer_callback_query(callback["id"])
    chat_id = callback["message"]["chat"]["id"]
    data = callback.get("data", "")
    if not data.startswith("faq:"):
        return

    faq_id = data.split(":", 1)[1]
    if faq_id == "list":
        send_faq_list(chat_id)
    elif faq_id in FAQ_BY_ID:
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
        telegram.send_message(chat_id, WELCOME.format(name=name), parse_mode="HTML",
                              reply_markup=faq_keyboard())
    elif command == "/faq":
        send_faq_list(chat_id)
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
