# AIP444 Lab 05 - Tool Calling with GitHub Context

Starting point: `pr-reader.py`, `SYSTEM_PROMPT.md`, and `requirements.txt` copied
from Lab 03, then extended for Phase 2. Lab 03 is unchanged. No secrets,
environments, caches, reports, or submission materials were copied. The source
tool and its original live evidence remain unchanged. Do not run the normal
PR workflow unless paid model requests are separately authorized.

## Setup and offline verification

From the repository root:

```powershell
python -m venv labs/lab-05/.venv
labs/lab-05/.venv/Scripts/python.exe -m pip install -r labs/lab-05/requirements.txt
labs/lab-05/.venv/Scripts/python.exe -B -m unittest discover -s labs/lab-05 -p test_tools.py -v
labs/lab-05/.venv/Scripts/python.exe -B -m unittest discover -s labs/lab-05 -p test_phase2.py -v
labs/lab-05/.venv/Scripts/python.exe -B labs/lab-05/pr-reader.py --test
```

During implementation these tests were run using the existing Lab 04 virtual
environment, whose requests and python-dotenv dependencies were already installed.
No files in Lab 04 were changed. All suites are offline: HTTP and model calls
are mocked. Phase 1 has 20 tests; the inherited PR Reader suite has 44, with API
and CLI fixtures updated to include fork-aware file_context. Phase 2 adds tests
for strict schemas, context enforcement, multi-turn history, errors, and limits.

## Phase 2 implementation

The complete supplied professor document was read from
`AIP444_Lab05_Official_Assignment.md`. Application logic changes are confined to
`pr-reader.py`; `tools.py` remains the Phase 1 implementation. Additional changes
are the system prompt, dependencies, this documentation, and new mocked tests.

`GitHubFile` and `ReadGitHubFilesParams` are strict Pydantic models. Every argument
field is required; only start_line/max_lines can be null. The application validates
JSON and converts null ranges to 1/500 before dispatch. The tool definition is
created with the SDK's `pydantic_function_tool()`. The chat transport remains
`requests.post()` against OpenRouter's chat-completions API; the helper generates
the schema, while application code performs validation and execution explicitly.

`fetch_pull_request()` extracts owner, repo, and ref from `head.repo.owner.login`,
`head.repo.name`, and `head.sha`. Forks work without guessing the base repository.
Missing/deleted head repos or invalid SHAs fail closed. Context is placed in the
escaped user prompt and a separate application system message; every file request
must exactly match it. The standalone Phase 1 tool remains usable with arbitrary
public repositories, but the LLM dispatcher cannot escape the trusted PR context.

The CLI still shows evidence before asking both student questions. Their answers
are preserved as entered, escaped for transport, and retained in every turn's
history. The loop sends the tool schema, appends each original assistant tool-call
message, then appends one tool result with its matching call ID. Multiple calls
per turn and successive tool rounds are supported. Malformed/unknown tool calls
and retrieval failures return safe tool errors; malformed IDs stop the protocol
rather than send unmatched results. Console logs show validated requests/ranges,
errors, completion, and the no-tool final response, never authentication headers.

Safety bounds: at most five model requests and ten tool calls per report; at most
five files per call. At the final request, further retrieval stops with an explicit
limit error instead of saving a fabricated report. Each file's formatted result
is limited to 100,000 source characters with an explicit partial-result notice.
These are bounds, not exact token-budget or spending caps. There are no automatic
model or HTTP retries. A model supporting strict function tools is required;
`openrouter/auto` availability does not guarantee support.

The Phase 1 function returns dictionaries. To satisfy the assignment's formatted
text requirement at the LLM boundary while preserving Phase 1, `format_tool_result`
turns them into XML-separated strings with escaped attributes, numbered content,
ref, range, total lines, and per-file errors. This phase uses the trusted commit
SHA, avoiding ambiguity in raw branch URLs. Phase 1's optional HEAD default is
never accepted as a model-requested substitute for the PR SHA.

The final report is checked for the five exact headings and three numbered
Learning questions. This verifies structure, not factual correctness or whether
a question is truly Socratic/unanswered; human review is still required. The
inherited direct `generate_report(prompt)` interface omits tools when no context
is supplied and rejects attempted tool calls. The current CLI always requires
trusted file_context and uses the complete tool loop.

## Remaining assignment evidence

No paid Phase 2 model trials have been run. For a separately authorized live
session, use `--session-dir sessions/CASE_NAME`. The application saves the original
interpretation/question in `initial.json` before the first model request, appends
actual requests/responses and tool events to `events.jsonl`, and saves the case's
`pr-report.md`. Session folders are Git-ignored for review before publication and
existing cases are never overwritten. The no-option workflow still keeps answers
only in memory; use the session option for assignment evidence. Suspected credential
patterns stop capture rather than writing secrets or silently rewriting answers.
See `LIVE_TEST_PLAN.md` and `PHASE3_PREPARATION.json` for the verified public cases.
The assignment requires two real PR cases: one needing tool context, one not.
Keep PR URLs, actual console logs, requested paths/SHAs/ranges, final five-section
reports, original answers, and the student's own revised understanding/evidence.
Try multiple models as required, document genuine iterations, and write personal
reflections. The final Word/PDF needs the GitHub link, commented tool code,
new prompt section, both cases' evidence, and the three assignment reflections.
No submission evidence or personal learning outcomes have been invented here.

## Tool input

`read_github_files(params)` in `tools.py` accepts a dictionary containing only a
`files` array. Each entry supports exactly these names:

```json
{
  "files": [
    {
      "owner": "requests",
      "repo": "toolbelt",
      "path": "requests_toolbelt/multipart/decoder.py",
      "ref": "HEAD",
      "start_line": null,
      "max_lines": null
    }
  ]
}
```

- `owner`, `repo`, `path`: required nonempty strings identifying a public file.
- `ref`: branch, tag, or commit; omitted/null defaults to `HEAD` (default-branch
  head). Prefer a specific commit SHA when evidence must be reproducible.
- `start_line`: omitted/null defaults to 1; otherwise an integer >= 1.
- `max_lines`: omitted/null defaults to 500; otherwise an integer from 1 to 5000.

Booleans, floating-point values, and numeric strings are not accepted as line
settings. Zero is rejected rather than treated as a missing value. Paths must be
relative without traversal, backslashes, or empty segments. URL components are
encoded so spaces, special filename characters, and slashes in refs remain data.

## Tool output

The return value is `{"files": [...]}` in input order. Each result has an `index`.
Valid specifications also carry `owner`, `repo`, `repository` (`owner/repo`),
`path`, `ref`, and `revision`. `revision` identifies the requested ref; a moving
branch is not resolved to an immutable SHA by this phase.

Successful downloads include:

- `total_lines`: total lines in the downloaded file, not just the selected slice.
- `requested_start_line`, `max_lines`: effective input settings.
- `start_line`, `end_line`: inclusive returned range, or null when no lines return.
- `lines`: dictionaries containing original `number` and `text` values.
- `content`: the same text prefixed with `N: ` line numbers for code reading.

Original indentation, trailing whitespace, and LF/CRLF/CR endings are retained.
An ending newline does not create an extra phantom line. An empty file has zero
lines, empty content, and a null range. Starting beyond a nonempty file returns
an `out_of_range` error, its total count, and an empty selection.

Invalid entries, HTTP errors, 403/429 rate-limit/access restrictions, timeouts,
connection failures, other request failures, and non-UTF-8/binary content produce
an `error` dictionary with a code and safe message. Failures do not abort later
files. A malformed outer dictionary raises ValueError. An empty files list is
valid and makes no requests. There are no automatic retries, authentication token
requirements, local file writes, or code execution in the tool. Redirects are
rejected rather than followed to another host.

## Standalone direct test

This performs public GitHub HTTP downloads only, with no LLM or paid API call:

```powershell
labs/lab-05/.venv/Scripts/python.exe -B labs/lab-05/test_tool.py --owner requests --repo toolbelt --path requests_toolbelt/multipart/decoder.py --ref HEAD --start-line 1 --max-lines 30
```

For multiple files, save a JSON input dictionary like the example above and use
`--params PATH_TO_JSON`. The standalone script prints JSON and exits nonzero if
any file result contains an error. Use `--help` for its options.

## Source-tool limitations

Phase 1 live raw-file results are preserved in LIVE_TOOL_TEST_RESULTS.json.
Branch names containing slashes are URL-encoding tested with mocks, not verified
against GitHub here.
The tool downloads each entire file to compute total lines, then slices it;
`max_lines` is an output limit, not a byte-download cap. Only UTF-8 source is
supported. HTTP 403 can indicate access restrictions as well as rate limiting.
No background waits or retries are performed.

Next: review the offline Phase 2 implementation, then explicitly authorize any
paid multi-turn model trials with an appropriate request/spending budget. A tool
session can involve multiple paid completions, not just a single model request.
