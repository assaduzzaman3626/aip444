"""Run manually against the local server; this can trigger a paid model request."""

import argparse
import json
from pathlib import Path
import time

import requests

from schemas import FlashcardResponse


def test_server(notes_path=None, cards=2):
    """Read notes, POST JSON, validate the response, and print it for inspection."""
    path = Path(notes_path) if notes_path else Path(__file__).with_name("notes.md")
    try:
        print(f"Reading notes from: {path}")
        notes = path.read_text(encoding="utf-8")
        print("Sending request to http://localhost:3000/api/generate ...")
        start = time.perf_counter()
        response = requests.post("http://localhost:3000/api/generate",
                                 json={"notes": notes, "cards": cards}, timeout=90)
        print(f"Request took {time.perf_counter() - start:.2f}s")
        if not response.ok:
            print(f"Server error HTTP {response.status_code}. Check the server terminal.")
            return 1
        result = FlashcardResponse.model_validate(response.json())
        if len(result.flashcards) != cards:
            raise ValueError("Unexpected card count")
        print("\n\u2705 Success! Received Structured Data:")
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, requests.exceptions.RequestException):
        print("Client failed. Check the notes path, running server, and response schema.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send notes to the running Lab 04 server.")
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--cards", type=int, default=2)
    args = parser.parse_args()
    raise SystemExit(test_server(args.notes, args.cards))
