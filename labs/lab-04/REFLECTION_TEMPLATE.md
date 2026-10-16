# Lab 04 — Student Submission Checklist

Status: implementation, 18 offline tests, two live model trials, and AI-assisted
server comments are prepared. See SUBMISSION_DRAFT.md for the assembled draft and
LIVE_TEST_RESULTS.md for original evidence. Student review/personalization,
an authentic screenshot, Word/PDF export, and GitHub push remain outstanding.

## Link to code

[Paste the GitHub labs/lab-04 folder link after committing and pushing.]

## Code-reading reflection — write this yourself

[Summarize what you learned about the server from the saved AI explanation and
your follow-up questions. Explain middleware, schemas, validation, and async work
in your own words.]

- [ ] Add your own opening comment block and inline comments to server.py.
- [ ] Ask for a suggestions-only review of your comments, then correct them yourself.

## Prompt changes

Implementation facts to discuss in your own explanation: Lab 02's role, source
grounding, acronym expansion, misconception, correction, and exact evidence rules
were retained. Plain-text field labels and delimiter rules were removed. The new
prompt describes JSON matching the schema and includes a JSON example.

[Explain your prompt changes and any actual testing issues in your own words.]

[Paste the complete SYSTEM_PROMPT.md into your final Word/PDF document.]

## Evidence of success

[Insert your own screenshot of the real test_client.py terminal showing Success!
and pretty-printed JSON. Do not substitute mocked output for a real model run.]

## Structured-output reflection — write this yourself

Completed trials: openai/gpt-4o-mini (5.41 seconds, USD 0.00026865) and
openai/gpt-4.1-mini (7.23 seconds, USD 0.0008808). Both passed structural and exact
quotation checks, but retained content-quality issues. Model and prompt both
changed, so these trials do not isolate the effect of the prompt refinement.

| Actual model ID | Result / errors | Card quality and evidence | Usage / cost if available |
| --- | --- | --- | --- |
| [First model actually tried] | [Your observations] | [Your assessment] | [Measured values] |
| [Second model actually tried] | [Your observations] | [Your assessment] | [Measured values] |

[What format issues did you actually encounter, and how did you overcome them?]

## Schema

[Paste the complete contents of schemas.py into the final Word/PDF document.]

## Final checks

- [ ] Re-run offline tests after your edits.
- [ ] Review files for secrets; do not include .env, .venv, or caches.
- [ ] Push the finished lab code to GitHub.
- [ ] Export your completed submission document to Word/PDF and submit on Blackboard.
