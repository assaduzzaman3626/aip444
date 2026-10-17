# Lab 05 Phase 3 - Prepared Live Cases

Status: public GitHub/model catalog verification only. No paid model requests,
student answers, tool-choice outcomes, or final reports have been generated.
Public evidence is saved in PHASE3_PREPARATION.json. Verification used no GitHub
or OpenRouter authentication token. Do not execute the paid CLI commands below
until a multi-turn model session has been explicitly authorized.

## Case A - Missing implementation context

- PR: https://github.com/requests/toolbelt/pull/399
- Title: Raise a specific error for missing boundaries
- Head repo: `ryanduguid/toolbelt` (public fork)
- Head SHA: `1a8c62f9992e0c96e73bb6801d1f634cad84f9d3`
- Verified HTTP 200: PR API, changed-files API, issue comments, actual diff, and
  pinned raw `requests_toolbelt/multipart/decoder.py`.
- Diff size: 10,271 characters; eight changed paths:

```text
AUTHORS.rst
HISTORY.rst
docs/decoding-data.rst
docs/index.rst
requests_toolbelt/__init__.py
requests_toolbelt/multipart/__init__.py
requests_toolbelt/multipart/decoder.py
tests/test_multipart_decoder.py
```

The diff shows new boundary checks and tests, but omits implementation bodies
needed to trace the constructor/from_response control flow and `_split_on_find`.
Tests and the author's claims do not substitute for inspecting those bodies when
the student's uncertainty concerns that flow or malformed boundary parameters.
At the verified head, the source file has 169 lines. Relevant locations include
`_split_on_find` at 17, constructor at 111, `_find_boundary()` call at 118,
`_parse_body()` call at 119, and `from_response` at 166.

Expected, not yet observed: the assistant requests relevant ranges in that exact
fork and SHA, then uses the returned code to address the student's actual gap.
For example, 105–169 covers construction and from_response; 1–35 covers the helper
if its behavior is relevant. These are planned ranges, not actual model requests.
The need for retrieval depends on the student's genuine unanswered question;
do not manufacture an interpretation or force a question simply to obtain a call.

## Case B - Self-contained docstring example correction

- PR: https://github.com/requests/toolbelt/pull/313
- Title: Fix MultipartEncoder docstring typo
- Head repo: `alexchen8/toolbelt` (public fork)
- Head SHA: `772ea644251acd3f0f106b42ab8287dcc7a06e69`
- Changed path: `requests_toolbelt/multipart/encoder.py` only.
- Verified HTTP 200: PR API, changed-files API, issue comments, actual diff, and
  the pinned head source file.
- Diff size: 660 characters; the description is absent.

The entire change replaces the comma between `'other_field'` and `'other_value'`
with a colon in a dictionary example in a class docstring. The immediate diff
context shows the surrounding MultipartEncoder call and dictionary. For a question
about what that syntax correction does, the diff is sufficient; no implementation
body is needed. The actual issue comments are retained in the preparation snapshot.

Expected, not yet observed: zero tool_request events and a final five-section
report grounded in the diff, with three unanswered Learning questions. If the
student asks about unrelated internals, retrieval could become justified instead;
record the actual behavior rather than claiming a predetermined no-tool result.

## Model and estimated cost

Verified via the public OpenRouter model and endpoint catalogs:

- ID: `openai/gpt-4o-mini`
- Available OpenAI endpoint lists `tools`, `tool_choice`, `structured_outputs`,
  and `response_format`; the application sets `provider.require_parameters=true`.
- Catalog price: USD 0.15 per million input tokens and USD 0.60 per million
  output tokens, before any other account/provider fees or price changes.
- Illustration: 5,000 input + 1,500 output tokens costs about USD 0.00165 for one
  completion. A tool session makes multiple completions and re-sends growing
  history, so this is not the price of the whole session or a spending cap.
- The app allows at most five model requests per session with no automatic retries.
  Endpoint availability and acceptance of this exact schema remain live-unverified.

Sources:
https://openrouter.ai/api/v1/models
https://openrouter.ai/api/v1/models/openai/gpt-4o-mini/endpoints

## Exact commands after authorization

Use PowerShell at the repository root. The existing Lab 04 virtual environment
already has requests, python-dotenv, openai, and pydantic, so these commands are
ready without installing into or modifying another lab. Python's `-B` avoids caches.
The root `.env` key is loaded by the app without printing it. Set only the model:

```powershell
$env:OPENROUTER_MODEL = "openai/gpt-4o-mini"
$env:PYTHONIOENCODING = "utf-8"
```

Case A:

```powershell
labs/lab-04/.venv/Scripts/python.exe -B labs/lab-05/pr-reader.py https://github.com/requests/toolbelt/pull/399 --session-dir sessions/case-a
```

Case B:

```powershell
labs/lab-04/.venv/Scripts/python.exe -B labs/lab-05/pr-reader.py https://github.com/requests/toolbelt/pull/313 --session-dir sessions/case-b
```

Read the evidence and type your own interpretation (2–4 sentences) and unanswered
question at the prompts. No answers are prefilled. Each case folder must be new;
use a new suffix for a separately authorized later trial rather than overwrite it.
The CLI fetches current PR metadata: if a head changes after preparation, the
session records its actual new SHA instead of silently claiming the one above.

## Evidence capture and security

`--session-dir` writes these files inside Lab 05:

- `initial.json`: PR URL, metadata with trusted context, comments, diff, original
  answer strings, and the escaped user prompt. This file is closed and saved
  before `generate_report()` can make its first model request.
- `events.jsonl`: ordered initial-save event, each model request's model/iteration,
  actual assistant messages (including raw call arguments), effective tool arguments
  with null defaults resolved, matching tool results, available usage, and final
  report or failure stage. Tool-request events include actual paths, refs, and ranges.
- `pr-report.md`: the returned and validated five-section report for that case.
  The usual top-level pr-report.md is also updated by the inherited workflow.

For Case B, absence of tool_request events together with assistant responses and
the final_report event documents a no-fetch run. For Case A, correlate call IDs,
effective arguments, returned source ranges, and the report's citations. Structural
checks cannot establish that analysis is correct or Learning questions are useful.

Headers, request objects, .env contents, and authentication values are never added
to records. Common credential patterns and the runtime API key are checked before
model events are saved; suspected credentials stop capture, not silently alter
the student's answer. Pattern scanning is a safeguard, not proof that every kind
of secret or private data is detectable. Manually review artifacts before publication.
The sessions directory is Git-ignored. Current preparation snapshots were scanned;
future live logs cannot be scanned until they actually exist.

## Offline verification commands (safe now)

```powershell
labs/lab-04/.venv/Scripts/python.exe -B -m unittest discover -s labs/lab-05 -p "test_*.py" -q
labs/lab-04/.venv/Scripts/python.exe -B labs/lab-05/pr-reader.py --test
```

Mocked tests verify answers exist on disk before generation, exact answer round
trips, no evidence overwrites, context enforcement, actual tool event fields,
report capture, and refusal to save suspected credentials. Test artifacts are
temporary, removed after tests, and are not presented as live results.
