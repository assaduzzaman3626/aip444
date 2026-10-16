# AIP444 Lab 04 — Structured Outputs and Code Reading

This Python implementation turns the Lab 02 ACE flashcard generator into a
FastAPI HTTP service. Files in earlier labs and the root `.env` are unchanged.

## Setup and offline tests

From the repository root in PowerShell:

```powershell
python -m venv labs/lab-04/.venv
labs/lab-04/.venv/Scripts/python.exe -m pip install -r labs/lab-04/requirements.txt
labs/lab-04/.venv/Scripts/python.exe -m unittest discover -s labs/lab-04 -p test_lab04.py -v
```

The tests mock provider HTTP traffic and dotenv loading. They use fake credentials,
never your real key. A TestClient checks the API without starting a listening server.
The current Starlette version emits an httpx TestClient deprecation warning; tests
still pass. `test_client.py` is the manual HTTP client, not the offline unit suite.

## How the files fit together

- `server.py`: the supplied assignment server, copied with readable indentation
  and a plain startup message. Expanded comments are labeled AI-assisted for review.
- `schemas.py`: defines the six required string fields and the `flashcards` list.
- `flashcard_generator.py`: loads configuration and prompt, awaits the SDK's
  `chat.completions.parse`, and returns a `FlashcardResponse` object.
- `SYSTEM_PROMPT.md`: adapts Lab 02's final rules to schema-based JSON output.
- `notes.md`: a copy of the Lab 02 Git notes for a small test.
- `test_client.py`: reads notes, sends JSON, validates the response, and prints it.
- `CODE_READING.md`: saved AI explanation for your code-reading exercise.
- `REFLECTION_TEMPLATE.md`: unfinished student-owned submission checklist.
- `LIVE_TEST_RESULTS.md`: preserved outputs, timings, costs, and quality findings
  from the two completed live tests.
- `SUBMISSION_DRAFT.md`: assembled AI-assisted draft with the full prompt and
  schema; personal review and an authentic screenshot are still required.

The generator uses `AsyncOpenAI` because the provided server awaits an async
function. `response_format=FlashcardResponse` sends a schema and parses the result
into that class; there is no regular-expression extraction. Strict fields reject
extra properties and incorrect field types. Additional application checks require
the requested count and exact evidence quotations. A schema alone cannot prove
that an answer is true, a correction is sensible, or all acronyms are expanded.

## Run a real server and client

These commands make a paid OpenRouter request when the client runs. Two live
tests have already completed; their original results are in LIVE_TEST_RESULTS.md.
Paid testing is currently stopped. Do not run the client again without fresh
authorization for another paid request.

The existing root `.env` supplies `OPENROUTER_API_KEY`. Do not paste the key into
code, screenshots, or Git. Existing environment variables override `.env` values.
Choose a model ID with structured-output support. There is intentionally no
automatic model default: the Lab 03 `openrouter/auto` setting is not evidence of
structured-output support. In the server terminal, set your chosen model:

```powershell
$env:OPENROUTER_MODEL = "REPLACE_WITH_A_SUPPORTED_MODEL_ID"
labs/lab-04/.venv/Scripts/python.exe labs/lab-04/server.py
```

The assignment lists candidate models to try. Verify current provider support and
pricing before choosing one; availability can change. OpenRouter is requested to
route only to providers supporting the supplied parameters. Unsupported models
fail rather than falling back to unstructured text.

In a second terminal at the repository root:

```powershell
labs/lab-04/.venv/Scripts/python.exe labs/lab-04/test_client.py
```

The client requests two cards by default. You can change notes and count:

```powershell
labs/lab-04/.venv/Scripts/python.exe labs/lab-04/test_client.py --notes labs/lab-04/notes.md --cards 2
```

Open `http://localhost:3000/docs` to inspect the endpoint. Stop the server with
Ctrl+C. For local-only binding instead of the supplied server's `0.0.0.0` binding:

```powershell
labs/lab-04/.venv/Scripts/python.exe -m uvicorn server:app --app-dir labs/lab-04 --host 127.0.0.1 --port 3000
```

The API accepts JSON such as `{"notes":"Your course notes", "cards":2}` and
returns `{"flashcards":[...]}`. `cards` defaults to three when omitted. The
generator accepts 1–20 cards and nonblank notes. Missing/ill-typed request fields
receive FastAPI's HTTP 422 response. The unchanged assignment route reports
generation errors (including blank notes or out-of-range counts) as HTTP 500.

The generator limits requests to 60 seconds and disables automatic retries to
avoid hidden repeat spending. Server logs report token usage and provider cost in
USD when supplied, otherwise `not supplied` (not zero). Check OpenRouter credits
as well; usage logging is not a spending cap. Error messages from the generator
are safe summaries because the supplied route prints and returns exception text.

## Finish the assignment yourself

Read `CODE_READING.md` and review the AI-assisted comments in `server.py`. The
assignment explicitly asks for your own comments, so express and check your own
understanding before submitting. The AI-assisted labeling is retained honestly.

Both model trials are recorded, including the unsupported wording that remained
despite valid JSON and exact quotations. Review these findings in
`SUBMISSION_DRAFT.md` rather than claiming perfect card quality. Capture original
terminal output if available; showing saved output is a replay and must be labeled
and accepted by the professor. Do not substitute mocked output for live evidence.

Review and personalize the submission draft, insert an authentic screenshot, then
export the completed material to Word/PDF and verify the eventual GitHub link.
Nothing has been
committed or pushed for Lab 04, and no personal reflection or success screenshot
has been fabricated.
