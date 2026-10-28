"""Сұраққа жауап беретін LLM-ді таңдау: Claude (кілт болса), әйтпесе Gemini."""

from bot import claude
from bot.gemini import ask_gemini


def ask_ai(question: str) -> str:
    if claude.is_configured():
        try:
            answer = claude.ask_claude(question)
            if answer:
                return answer
        except Exception as e:
            # Баланс таусылса, кілт қате болса немесе Claude бос болмаса — Gemini жауап береді.
            print(f"Claude failed, falling back to Gemini: {e!r}")
    return ask_gemini(question)
