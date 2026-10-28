"""Claude (Anthropic) арқылы химиялық сұрақтарға жауап беру."""

import os

import anthropic

from bot.prompt import SYSTEM_PROMPT

DEFAULT_MODEL = "claude-opus-5-5"

_client = None


def is_configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _get_client():
    global _client
    if _client is None:
        # Vercel функциясының уақыты шектеулі: Claude кешіксе, Gemini-ге ауысуға уақыт қалсын.
        _client = anthropic.Anthropic(timeout=35.0, max_retries=0)
    return _client


def ask_claude(question: str) -> str:
    response = _get_client().messages.create(
        model=os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL),
        max_tokens=16000,
        output_config={"effort": "medium"},
        # Ұзын system prompt әр сұрақта бірдей — кэш арзанырақ әрі жылдамырақ.
        cache_control={"type": "ephemeral"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude refused: {response.stop_details}")
    return "".join(b.text for b in response.content if b.type == "text").strip()
