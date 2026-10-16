"""Generate validated objects through the OpenAI SDK's OpenRouter endpoint."""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from schemas import FlashcardResponse

logger = logging.getLogger("uvicorn.error")
LAB_DIR = Path(__file__).resolve().parent


async def generate_flashcards(notes: str, cards: int) -> FlashcardResponse:
    """Return validated cards, failing safely instead of parsing text with regex."""
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("Provide nonempty course notes.")
    if type(cards) is not int or not 1 <= cards <= 20:
        raise ValueError("Request between 1 and 20 cards.")

    load_dotenv(LAB_DIR.parent.parent / ".env", override=False)
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "").strip()
    if not key:
        raise RuntimeError("Missing OPENROUTER_API_KEY configuration.")
    if not model:
        raise RuntimeError("Set OPENROUTER_MODEL to a model supporting structured outputs.")
    try:
        prompt = (LAB_DIR / "SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise RuntimeError("Could not read Lab 04 SYSTEM_PROMPT.md.") from None
    if not prompt.strip():
        raise RuntimeError("Lab 04 SYSTEM_PROMPT.md is empty.")

    try:
        async with AsyncOpenAI(
            api_key=key, base_url="https://openrouter.ai/api/v1",
            timeout=60.0, max_retries=0,
        ) as client:
            completion = await client.chat.completions.parse(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps({"cards": cards, "notes": notes}, ensure_ascii=False)},
                ],
                response_format=FlashcardResponse,
                extra_body={"provider": {"require_parameters": True}},
            )
    except Exception:
        # The supplied server prints exceptions; never propagate provider text or keys.
        raise RuntimeError("Flashcard provider request failed or returned invalid structured output. Check model support, credits, and connection.") from None

    usage = completion.usage
    if usage is not None:
        details = usage.model_dump()
        logger.info("Generation usage: prompt_tokens=%s completion_tokens=%s cost_usd=%s",
                    details.get("prompt_tokens"), details.get("completion_tokens"),
                    details.get("cost", "not supplied"))
    if not completion.choices:
        raise RuntimeError("The model returned no choices.")
    message = completion.choices[0].message
    if message.refusal:
        raise RuntimeError("The model declined to generate these flashcards.")
    result = message.parsed
    if not isinstance(result, FlashcardResponse):
        raise RuntimeError("The model returned no validated flashcards.")
    if len(result.flashcards) != cards:
        raise RuntimeError("The model did not generate the requested number of supported cards.")
    if any(card.evidence not in notes for card in result.flashcards):
        raise RuntimeError("A generated evidence quotation does not match the source notes.")
    return result
