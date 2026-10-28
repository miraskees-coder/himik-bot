"""Gemini LLM арқылы химиялық сұрақтарға жауап беру."""

import os

from google import genai
from google.genai import types

from bot.faq import faq_context

DEFAULT_MODEL = "gemini-flash-lite-latest"
FALLBACK_MODEL = "gemini-flash-latest"

SYSTEM_PROMPT = f"""Сен — «ХИМИК», химия бойынша Telegram көмекші-ботсың.

Ережелер:
- Тек химияға қатысты сұрақтарға жауап бер (химиялық ұғымдар, элементтер, реакциялар,
  теңдеулер, есептер, зертхана, химияның тарихы мен қолданылуы).
- Химияға қатысы жоқ сұрақтарға сыпайы түрде: «Кешіріңіз, мен тек химия бойынша
  сұрақтарға жауап беремін 🧪» деп жауап бер.
- Пайдаланушы қай тілде жазса, сол тілде жауап бер (әдепкі — қазақ тілі).
- Жауабың қысқа, нақты және оқушыға түсінікті болсын. Есептерді қадамдап шығар.
- Формулаларда төменгі индекстерді Unicode арқылы жаз (H₂O, CO₂, H₂SO₄).
- Markdown белгілерін (**, #, `) қолданба — жауап қарапайым мәтін ретінде көрсетіледі.
- Жарылғыш заттарды, улы заттарды, есірткі немесе қаруды дайындау нұсқаулығын ешқашан берме.

Боттың дайын FAQ тақырыптары (пайдаланушыға /faq командасын ұсынуға болады):
{faq_context()}
"""

_client = None


def _get_client():
    global _client
    if _client is None:
        # Қайталауды азайтамыз: модель бос болмаса, резервке тез ауысқан дұрыс
        # (Vercel функциясының уақыты шектеулі).
        _client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options=types.HttpOptions(
                timeout=20_000,
                retry_options=types.HttpRetryOptions(attempts=2),
            ),
        )
    return _client


def _generate(model: str, question: str) -> str:
    response = _get_client().models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4,
            max_output_tokens=2048,
        ),
    )
    return (response.text or "").strip()


def ask_gemini(question: str) -> str:
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    try:
        return _generate(model, question)
    except Exception as e:
        # Негізгі модель бос емес/қолжетімсіз болса (503, 404) — жеңіл модельмен қайталаймыз.
        if model == FALLBACK_MODEL:
            raise
        print(f"Gemini {model} failed, falling back to {FALLBACK_MODEL}: {e!r}")
        return _generate(FALLBACK_MODEL, question)
