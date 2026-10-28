# ХИМИК 🧪 — химия бойынша Telegram бот

Химия бойынша сұрақтарға және есептерге жауап береді. `ANTHROPIC_API_KEY` қойылса — Claude арқылы, әйтпесе (немесе Claude істемесе) — Gemini арқылы. Vercel-де serverless (webhook) режимінде жұмыс істейді.

## Құрылымы

```
api/webhook.py       Telegram хабарларын қабылдайтын endpoint
api/set_webhook.py   Webhook-ты бір рет тіркеу
bot/faq.py           FAQ сұрақ-жауаптары (осы жерден өзгертуге/қосуға болады)
bot/ai.py            Модель таңдау: Claude → Gemini → FAQ
bot/claude.py        Claude-қа сұрау
bot/gemini.py        Gemini-ге сұрау
bot/prompt.py        «ХИМИК» нұсқауы (system prompt)
bot/handlers.py      Командалар мен хабарларды өңдеу
bot/telegram.py      Telegram Bot API шақырулары
```

## Vercel-ге орналастыру

1. Жобаны GitHub-қа жүктеңіз, содан кейін [vercel.com](https://vercel.com) → **Add New → Project** → репозиторийді таңдаңыз → **Deploy**.
   (Немесе терминалда: `npm i -g vercel` → `vercel --prod`)
2. Кілттер жергілікті `.env` файлында сақталады. Ол `.gitignore`-да тұр, сондықтан GitHub-қа жүктелмейді, демек Vercel оны көрмейді.
   Сондықтан `.env` ішіндегі барлық мәтінді көшіріп, Vercel → Project → **Settings → Environment Variables** бөлімінің Key өрісіне қойыңыз (Vercel барлық айнымалыны бірден таниды):
   - `TELEGRAM_BOT_TOKEN` — BotFather берген токен
   - `GEMINI_API_KEY` — Gemini API кілті
   - `TELEGRAM_SECRET_TOKEN` — өзіңіз ойлап тапқан құпия сөз (тек әріп, сан, `_`, `-`)
   - `ANTHROPIC_API_KEY` — міндетті емес, Claude кілті (platform.claude.com)
   - `GEMINI_MODEL` — міндетті емес (әдепкі `gemini-flash-lite-latest`)
3. **Deployments → Redeploy** басыңыз (айнымалылар күшіне енуі үшін).
4. Браузерде бір рет ашыңыз:
   ```
   https://<сіздің-жоба>.vercel.app/api/set_webhook?secret=<TELEGRAM_SECRET_TOKEN>
   ```
   Жауапта `"ok": true` болуы керек.
5. Telegram-да ботқа `/start` жазыңыз 🎉

## Тексеру

- `https://<сіздің-жоба>.vercel.app/api/webhook` — «ХИМИК бот жұмыс істеп тұр» деп шығуы керек.
- `https://api.telegram.org/bot<TOKEN>/getWebhookInfo` — `last_error_message` болмауы керек.
- Қателер: Vercel → Project → **Logs**.

## FAQ қосу

`bot/faq.py` файлындағы `FAQ` тізіміне жаңа жазба қосыңыз:

```python
{
    "id": "unique_id",          # латынша, қайталанбайтын
    "question": "Сұрақ мәтіні?",
    "answer": "Жауап (HTML: <b>, <i> қолдануға болады)",
    "keywords": ["кілт сөз", "тағы бір"],
},
```
