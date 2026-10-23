# Assignment 1: AI Code Review

A Python CLI that reviews staged Git changes or individual files with **two parallel AI reviewers** and a **third AI judge**. Uses the OpenAI SDK pointed at OpenRouter.

## Prerequisites

- Python 3.10+ and Git
- [OpenRouter](https://openrouter.ai/) API key and credits
- [ripgrep](https://github.com/BurntSushi/ripgrep) installed (`rg --version`)

## Setup (Windows PowerShell)

Open a terminal **inside** your course repository under `assignments/assignment-01`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
rg --version
$env:OPENROUTER_API_KEY = 'YOUR_KEY'  # enter locally; never commit
```

**Security:** never put your key in `review.py`, screenshots, commits, or Blackboard documents. Do not paste the key into chat. `.env` is gitignored, but this CLI reads `OPENROUTER_API_KEY` from the process environment.

## Run

```powershell
python review.py --debug --file bad_code.py --output golden-report.html
python review.py --file bad_code.py
# Git Mode, after staging a small change:
git status
git add README.md
python review.py --debug --output git-report.html
python review.py
```

For Git Mode, a new `README.md` must be staged as a change; after committing, edit one line before `git add README.md`. Debug logs go to **stderr** and final status/output path goes to **stdout**. To capture both:

```powershell
python review.py --debug --file bad_code.py 2>&1 | Tee-Object golden-debug.txt
```

Adjust models through environment variables if chosen models do not support both tool calling and structured outputs. Defaults: reviewer `openai/gpt-4.1-mini`; judge `openai/gpt-4.1`. Two different model IDs are mandatory. Pricing, availability, structured-output and tool support may change; verify on OpenRouter before a paid run.

## How it works

1. Read file contents or staged `git diff --staged`.
2. Run Security Auditor and Maintainability Critic concurrently using `asyncio.gather`.
3. Permit bounded `read_file` and `ripgrep` tool calls; send tool results back to each AI reviewer.
4. Validate JSON findings with a strict `response_format` schema.
5. Give both sets of findings and original input to a different judge model.
6. Produce a standalone HTML report. `--debug` logs requests, tool responses, and reviewer JSON.

## Evidence checklist

- Screenshot Golden Dataset: `python review.py --debug --file bad_code.py` showing tool logs, JSON, and saved report. Open HTML report and screenshot.
- Screenshot Git Mode: `git status` with staged changes, then `python review.py --debug`; also run without `--debug`.
- Record models actually tested, token usage, OpenRouter billed costs, latency, findings, and any mistakes.
- Submit Word/PDF with GitHub folder link, both evidence screenshots and reflection. Confirm professor is a collaborator.

## Limitations

The reviewer uses your current working tree for context and truncates large inputs/files. Staged diffs may differ from unstaged working-tree files. The LLM may produce false positives and the judge may fail to filter them; verify all findings manually. Code content is transmitted to OpenRouter/models: avoid confidential repositories. Keep credit costs under control.

Note: the initial model turn requires at least one tool call from each reviewer and the judge, to make tool use observable. The provider/model must support tool_choice=required.
