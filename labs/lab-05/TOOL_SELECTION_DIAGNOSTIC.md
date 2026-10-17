# Lab 05 Tool-Selection Diagnostic

This is an evidence audit, not a new live trial or the student's reflection.
No paid request was made during this diagnostic. Historical sessions are unchanged.

## Finding and confidence

No client-side dispatch or serialization defect was reproduced. The preserved
responses for both cases ended with finish_reason=stop and omitted tool_calls.
Each returned report text immediately. Therefore these records show no tool call
that the application failed to detect or execute.

The exact reason the model chose not to retrieve is UNVERIFIED. A plausible
explanation is that it treated the supplied diffs/descriptions as sufficient for
the explanation it chose to give. In places it also made broad assertions instead
of identifying and resolving an evidence gap. That is observed report-quality
behavior, not evidence of the model's private decision process.

## Historical evidence

| Session | Saved request metadata | Actual response | Actual tool executions |
| --- | --- | --- | --- |
| sessions/case-a (PR 399) | model_request: iteration 1, openai/gpt-4o-mini | finish_reason=stop; no tool_calls field; final Markdown | 0 |
| sessions/case-a-393 (PR 393) | model_request: iteration 1, openai/gpt-4o-mini | finish_reason=stop; no tool_calls field; final Markdown | 0 |

The PR 393 run summary records tool_choice=auto, but neither event log contains
the serialized request schema, provider preferences, exact system-prompt hash,
or returned provider identity. Current source and offline tests corroborate the
intended payload; they do not retroactively prove what an upstream provider
received during those historical calls. No missing historical fields were added
to the original records or presented as captured evidence.

## Outgoing schema and selection

GitHubFile and ReadGitHubFilesParams have extra=forbid and strict runtime types.
The SDK pydantic_function_tool helper generates a function named read_github_files
with strict=true, required files, all six required per-file fields, nullable
start_line/max_lines, and their numeric bounds. The serialized schema contains
the expected object definitions and references; no Python class objects appear
in its JSON representation.

With trusted file_context, every completion includes tools, tool_choice=auto,
and provider.require_parameters=true. It also includes API-derived owner/repo/SHA
in an application system message. The CLI supplies this context. The inherited
context-free direct interface intentionally omits tools and rejects attempted
tool calls, but that interface was not used in either preserved live session.

No forced selection, PR-number branch, mandatory fetch, provider pinning, or
automatic paid retry was added.

## Compatibility verification

The current public endpoint catalog lists an OpenAI endpoint for openai/gpt-4o-mini
supporting tools, tool_choice, structured_outputs, and response_format. Other
listed endpoints differ in their supported-parameter lists, so model-wide support
is not by itself proof of endpoint behavior. require_parameters=true is already
set in the application. The selected historical provider was not captured.

Sources checked during the audit:

- https://openrouter.ai/api/v1/models/openai/gpt-4o-mini/endpoints
- https://openrouter.ai/docs/guides/features/tool-calling

Published support does not guarantee that a live model will choose a tool, or
establish whether this exact schema was enforced by a historical provider.

## Diff sufficiency and prompt review

PR 399: the broad original question concerns effects elsewhere in the program.
The description already identifies the exception-type compatibility break, and
the diff shows the export changes and tests. That supports a narrow no-fetch
answer. A helper-tokenization or omitted constructor-path question would require
more source, but that was not the student's original question. The report's
compatibility overstatements and weak citations should not be mistaken for proof
that retrieval was impossible or unnecessary for every possible conclusion.

PR 393: the actual diff includes _reset's state assignments, per-part reset,
read-byte tracking, seek/tell, monitor changes, and repeated-read tests. Much of
the student's rewind-state question can be addressed directly from those changes.
Unchanged coercion/adaptation code could improve a deeper trace, but the model
instead gave a short summary and left reprocessing insufficiently explained.
No retrieval benefit can be claimed from that run.

The current prompt deliberately discourages unnecessary calls and requires a
specific material evidence gap. It also explicitly permits read_github_files
under trusted context constraints, despite prohibiting arbitrary link-following.
There is no blanket prohibition on retrieving encoder/decoder source. Some
conservatism in that wording may influence selection, but this has not been
isolated experimentally. The prompt had already been refined; no further prompt
change is justified by these diagnostics alone.

## Detection and multi-turn verification

The application checks message.tool_calls independently of finish_reason. Calls
are validated before dispatch; the original assistant message and every matching
tool result are retained in history. Multiple calls and multiple turns work in
offline tests. Schema, routing and auto selection remain present on follow-ups.
Bad arguments produce a matching tool error and can be corrected in a later turn.

Three new transport tests use real requests serialization and response decoding,
but intercept Session.send before any network I/O. They verify:

1. The actual prepared JSON body contains the strict schema, auto selection,
   trusted context and require_parameters setting; a no-call response makes no
   source request.
2. Two calls in one response followed by another tool round produce three actual
   mocked raw-file reads, correct original line numbers, IDs, and complete history.
3. Malformed arguments produce a matched error without fetching, then a corrected
   call succeeds through the unchanged Phase 1 retrieval function.

These establish application wiring and protocol behavior, not live model judgment.

## Minimal observability fix

Future model_request events additionally record the actual public tool definitions,
tool_choice, provider preferences, trusted file_context, message-role sequence,
and system-prompt/tool-schema SHA-256 hashes. They exclude headers, API credentials,
and prompt/answer text. Existing initial.json continues preserving student input.

Future assistant_response events also record HTTP status and response provider,
model, and response ID when supplied (null means unavailable). Existing safe
credential checks apply before saving events. Historical logs are not backfilled.

## Verification and remaining work

- 37 Phase 2/session/transport tests passed.
- 20 Phase 1 tool tests passed.
- 44 inherited PR Reader tests passed.
- Total: 101 offline tests passed.

Both historical cases remain no-tool outcomes. A successful context-used live
demonstration remains outstanding; it cannot be manufactured through mocks or
forced choice. Any further paid trial requires separate authorization and should
use a genuine student uncertainty that materially depends on omitted code. Keep
all earlier outcomes and compare both semantic quality and actual retrieval.
