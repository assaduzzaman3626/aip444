"""AIP444 Lab 02 - ACE flashcard generator using source-locked evidence."""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "google/gemma-3-27b-it"
MAX_ATTEMPTS = 3
MAX_EXCERPTS = 75
FIELDS = ("application", "challenge", "answer", "evidence_id", "misconception", "correction")


def read_file(path, description):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"Cannot read {description}: {path} ({exc})") from exc
    except UnicodeError as exc:
        raise ValueError(f"{description} is not valid UTF-8: {path}") from exc


def evidence_candidates(notes):
    """Extract exact, contiguous, one-line passages from original notes."""
    items = []
    seen = set()
    in_code = False
    for raw in notes.splitlines():
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith(("#", "<!--", "|", "[!")):
            continue
        # Prefer complete sentences; never rewrite or normalize their characters.
        spans = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'`*])", line)
        for span in spans:
            span = span.strip()
            if span.startswith(("- ", "* ", "> ")):
                span = span[2:].strip()
            if len(span) < 40:
                continue
            # Keep longer original lines when a sentence is too long.
            if len(span) > 340:
                continue
            if span not in notes or span in seen:
                continue
            seen.add(span)
            items.append(span)
    # Spread excerpts across the document, not just its first section.
    if len(items) > MAX_EXCERPTS:
        indices = [int(i * (len(items) - 1) / (MAX_EXCERPTS - 1))
                   for i in range(MAX_EXCERPTS)]
        items = [items[i] for i in indices]
    return {f"E{i}": value for i, value in enumerate(items, 1)}


def parse_json_response(raw):
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, count=1)
        text = re.sub(r"\s*```$", "", text, count=1)
    return json.loads(text)


def validate(result, wanted, excerpts):
    if not isinstance(result, dict) or not isinstance(result.get("cards"), list):
        return None, "Response must be a JSON object with a cards array."
    cards = result["cards"]
    if len(cards) != wanted:
        return None, f"Expected {wanted} cards but received {len(cards)}."
    used_ids = set()
    for i, card in enumerate(cards, 1):
        if not isinstance(card, dict) or set(card) != set(FIELDS):
            return None, f"Card {i}: wrong or missing JSON fields."
        if any(not isinstance(card[k], str) or not card[k].strip() for k in FIELDS):
            return None, f"Card {i}: fields must be nonempty strings."
        eid = card["evidence_id"].strip()
        if eid not in excerpts:
            return None, f"Card {i}: unknown evidence ID {eid!r}."
        if eid in used_ids:
            return None, f"Card {i}: duplicate evidence ID {eid}."
        used_ids.add(eid)
        # Strip any unnecessary surrounding quotation marks from a misconception.
        # The final ACE rendering adds exactly one pair.
        card["misconception"] = card["misconception"].strip().strip('"“”')
        if not card["misconception"]:
            return None, f"Card {i}: empty misconception."
    return cards, None


def make_messages(system_prompt, excerpts, count):
    evidence_lines = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                               for key, value in excerpts.items())
    system = ("You create educational ACE flashcards based ONLY on supplied course excerpts. "
              "The user's SYSTEM_PROMPT.md specifies pedagogical goals and content style, "
              "but the program constructs the final ACE formatting and evidence itself. "
              "For this API stage, return only valid JSON; no Markdown or explanation. "
              "Use evidence_id values exactly as supplied; do not copy quotation text. "
              "Every answer and correction must be supported by its selected evidence. "
              "Expand acronyms in the answer; misconceptions should sound like confused students.\n\n"
              "Course prompt guidance:\n" + system_prompt)
    user = (f"Create exactly {count} distinct ACE cards from these source excerpts. "
            "Each card must use one different evidence_id. "
            "Return strictly this JSON shape: "
            '{"cards":[{"application":"...","challenge":"...","answer":"...",'
            '"evidence_id":"E1","misconception":"I thought ...",'
            '"correction":"..."}]}. '
            "Use six named properties per card exactly. The selected evidence must directly "
            "support the answer, not merely relate to its topic. "
            "If the excerpts do not support the requested number of distinct cards, "
            'return {"error":"Insufficient information to generate the requested cards."}.\n\n'
            "SOURCE EXCERPTS (exact source strings identified by ID):\n" + evidence_lines)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def render(cards, excerpts):
    for i, card in enumerate(cards, 1):
        quote = excerpts[card["evidence_id"].strip()]
        print(f"=== CARD {i} ===")
        print(f'-APPLICATION: {card["application"].strip()}')
        print(f'-CHALLENGE: {card["challenge"].strip()}')
        print(f'-ANSWER: {card["answer"].strip()}')
        print(f'-EVIDENCE: "{quote}"')
        print(f'-MISCONCEPTION: "{card["misconception"]}"')
        print(f'-CORRECTION: {card["correction"].strip()}')
        print("===\n")


def main():
    print("AIP444 Fall 2026 - Lab 02")
    print("flashcards: MD ASSADUZZAMAN - 122963242")
    print("Run Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("----------------------------------------------")

    parser = argparse.ArgumentParser(description="Generate source-grounded ACE flashcards")
    parser.add_argument("notes_path", help="Path to .md, .txt or .html notes")
    parser.add_argument("--cards", type=int, default=3, help="Number of cards (1-5)")
    args = parser.parse_args()
    if not 1 <= args.cards <= 5:
        parser.error("--cards must be between 1 and 5")

    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found.")
        return 1
    print("✅ OpenRouter API key found")
    print("Notes file:", args.notes_path)
    print("Number of cards:", args.cards)

    try:
        prompt = read_file(Path(__file__).with_name("SYSTEM_PROMPT.md"), "system prompt")
        notes = read_file(args.notes_path, "notes file")
    except ValueError as exc:
        print("❌ Error:", exc)
        return 1
    print("✅ System prompt loaded successfully")
    print("✅ Course notes loaded successfully")
    print("Notes length:", len(notes), "characters")
    if not notes.strip() or not re.sub(r"[#\s]", "", notes):
        print("❌ Error: The notes are empty. Please provide useful course notes.")
        return 1
    if not prompt.strip():
        print("❌ Error: SYSTEM_PROMPT.md is empty.")
        return 1

    excerpts = evidence_candidates(notes)
    if len(excerpts) < args.cards:
        print("❌ ERROR: Insufficient information to generate the requested cards.")
        print(f"Only {len(excerpts)} usable evidence passages found for {args.cards} cards.")
        return 1

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key,
                    timeout=90.0, max_retries=1)
    messages = make_messages(prompt, excerpts, args.cards)
    print(f"✅ Prepared {len(excerpts)} exact source excerpts")
    print("\n🤖 Generating flashcards...")
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt} of {MAX_ATTEMPTS}")
        try:
            response = client.chat.completions.create(
                model=MODEL, temperature=0.2, messages=messages
            )
            output = response.choices[0].message.content or ""
        except Exception as exc:
            print("❌ OpenRouter API error:", exc)
            return 1

        try:
            result = parse_json_response(output)
        except (ValueError, TypeError) as exc:
            error = f"Invalid JSON response: {exc}"
        else:
            if isinstance(result, dict) and "error" in result:
                print("❌ ERROR:", result["error"])
                return 1
            cards, error = validate(result, args.cards, excerpts)
            if error is None:
                print("✅ Format and evidence ID checks passed.")
                print(f"\n✅ Generated {len(cards)} flashcard(s):\n")
                render(cards, excerpts)
                return 0

        print("⚠️ Validation failed:", error)
        if attempt < MAX_ATTEMPTS:
            messages.append({"role": "assistant", "content": output})
            messages.append({"role": "user", "content":
                             f"Your last JSON failed validation: {error}. "
                             "Return corrected JSON with exactly the requested cards "
                             "and valid, distinct evidence_id values; no other text."})
            print("🔄 Requesting a corrected response...")
    print("❌ Unable to generate validated flashcards after 3 attempts.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
