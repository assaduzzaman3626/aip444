# AIP444 Lab 03: PR Reading Partner

Install dependencies and run the offline test suite from the repository root:

```powershell
labs/lab-03/.venv/Scripts/python.exe -m pip install -r labs/lab-03/requirements.txt
labs/lab-03/.venv/Scripts/python.exe labs/lab-03/pr-reader.py --test
```

`generate_report(user_prompt)` accepts the string produced by `build_user_prompt()`
and returns OpenRouter's Markdown response. It reads the complete UTF-8
`SYSTEM_PROMPT.md` beside the script and loads the repository-root `.env` using
python-dotenv. Existing environment values take precedence. The key is never
printed; no key belongs in this README or source code.

Configuration:

- `OPENROUTER_API_KEY`: required, supplied through the existing root `.env` or environment.
- `OPENROUTER_MODEL`: optional, defaults to `openrouter/auto` (OpenRouter chooses
  the model). Set a specific OpenRouter model ID to choose it explicitly.

The request uses a 60-second timeout. Failures raise `RuntimeError` with a safe
message instead of exposing provider response bodies or request headers.
Calling `generate_report()` sends the supplied PR material and student answers
to OpenRouter. The `--test` option runs mocked tests without reading your key,
contacting GitHub or OpenRouter, or writing a real report.

## Run the application

From the repository root, supply a public PR URL (replace the example):

```powershell
labs/lab-03/.venv/Scripts/python.exe labs/lab-03/pr-reader.py https://github.com/OWNER/REPO/pull/123
```

Or leave out the URL and the application will ask for it:

```powershell
labs/lab-03/.venv/Scripts/python.exe labs/lab-03/pr-reader.py
```

The application downloads the PR details, up to 100 issue comments, and the diff.
It displays the title, description, and up to 12,000 diff characters at a time.
If more diff is available, type `m` to keep reading, or press Enter to move to
the questions. Read enough of the actual code changes to form your own opinion.
Diffs longer than 95,000 characters are truncated with a warning.

Next, write what you think the PR changes and why in 2–4 sentences, then name
one thing you do not understand. Blank answers are retried; your accepted answers
are kept exactly as typed. Only after both answers does the application send the
evidence and answers to OpenRouter. This normal application run makes real network
requests and may incur model charges; use `--test` for offline testing.

The Markdown report is printed and saved as `labs/lab-03/pr-report.md`, replacing
an existing report at that location. Its five sections are `tl;dr`,
`Your Understanding`, `Changes`, `Discussion`, and `Learning`. The system prompt
requests these sections; model output is not automatically repaired.
The save location is based on the script's folder, even if you run it elsewhere.
Errors return a nonzero exit code; Ctrl+C cancels the session.
