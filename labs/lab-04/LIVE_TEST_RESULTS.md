# Lab 04 First Live Test

- Model: `openai/gpt-4o-mini`
- Credentials: repository-root `.env` (existing environment values retain precedence); available, value withheld.
- Input: `notes.md`; requested cards: 2.
- SDK automatic retries: 0; client launched once.
- Outcome: SUCCESS
- Server stopped: True
- Client process elapsed time: 5.816 seconds (includes startup and HTTP request).
- Client reported Success!: PASS
- Exactly two flashcards: PASS
- All six fields, with nonempty string values, on every card: PASS
- Every evidence quotation matches notes.md exactly: PASS

## Actual client output

```text
Reading notes from: C:\Users\assad\OneDrive\Desktop\aip444\labs\lab-04\notes.md
Sending request to http://localhost:3000/api/generate ...
Request took 5.41s

✅ Success! Received Structured Data:
{
  "flashcards": [
    {
      "application": "A developer is preparing updates to a software project and wants to track which changes will be stored.",
      "challenge": "How can the developer prepare changes to be recorded in the repository history?",
      "answer": "The git add command places changes in the staging area, preparing them for the next commit.",
      "evidence": "The git add command places changes in the staging area.",
      "misconception": "\"I can use git commit without using git add first.\"",
      "correction": "The notes indicate that the git commit command records changes that are already staged by git add, so it can't be used alone."
    },
    {
      "application": "A programmer is ready to finalize their changes in a project after staging them.",
      "challenge": "What command should the programmer execute to save their staged changes to the repository history?",
      "answer": "The git commit command records staged changes in the repository history, permanently saving them.",
      "evidence": "The git commit command records staged changes in the repository history.",
      "misconception": "\"The git commit command only shows the changes made to files.\"",
      "correction": "The notes clarify that the git commit command records changes, not just displays them."
    }
  ]
}

```

## Actual server output

```text
INFO:     Started server process [34316]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
INFO:     Generation usage: prompt_tokens=867 completion_tokens=231 cost_usd=0.00026865
INFO:     127.0.0.1:59823 - "POST /api/generate HTTP/1.1" 200 OK

```

## Errors and quality observations

The API and client completed successfully. After the results were saved, the
outer test runner encountered a Windows cp1252 UnicodeEncodeError while printing
the success checkmark. The saved UTF-8 record was read successfully afterward;
no second API request was made. Port 3000 was confirmed no longer listening.

Schema and exact-quotation checks passed, but content quality still needs review.
The first correction says git commit cannot be used alone, which overgeneralizes:
previously staged changes can be committed without a new git add invocation.
The second answer's phrase "permanently saving" is stronger than the source notes
support. These are useful observations for the student's model-quality reflection;
structural success does not establish perfect factual grounding.

---

# Lab 04 Live Test 2 ? Improved Prompt

- Model: `openai/gpt-4.1-mini`
- Input: `notes.md`; two flashcards requested.
- Prompt SHA-256: `15d3197ccc5cf03230fc7b63b2fd1722ce14aeea6297060c343eb030c0cec01e`
- SDK automatic retries: 0; one client run; no retry.
- Outcome: SUCCESS
- HTTP 200 confirmed: True
- Server stopped: True
- Client process elapsed time: 7.765 seconds (including process startup).
- Success! with zero client exit code: PASS
- Exactly two flashcards: PASS
- Six nonempty string fields on every card: PASS
- Card 1 evidence is an exact notes substring: PASS
- Card 2 evidence is an exact notes substring: PASS

## Full unmodified client output

```text
Reading notes from: C:\Users\assad\OneDrive\Desktop\aip444\labs\lab-04\notes.md
Sending request to http://localhost:3000/api/generate ...
Request took 7.23s

✅ Success! Received Structured Data:
{
  "flashcards": [
    {
      "application": "A developer is working on a project and has modified several files. They want to prepare the changes for saving in the project history.",
      "challenge": "Which Git command should they use to place their file changes into the staging area before committing?",
      "answer": "The git add command places changes in the staging area, preparing them for the next commit.",
      "evidence": "The git add command places changes in the staging area.",
      "misconception": "\"I can record my changes directly to the repository history without using git add first.\"",
      "correction": "According to the notes, git add is necessary to place changes in the staging area before git commit records them in the repository history."
    },
    {
      "application": "A programmer wants to check which changes have been staged and the current situation of their project files before saving them permanently.",
      "challenge": "Which command should the programmer use to see the current state of the repository including staged changes?",
      "answer": "The git status command shows the current state of the repository, including information about staged and unstaged changes.",
      "evidence": "The git status command shows the current state of the repository.",
      "misconception": "\"git status will save all my current changes automatically.\"",
      "correction": "The notes specify that git status only shows the current state and does not save any changes."
    }
  ]
}

```

## Full server output (includes reported cost)

```text
INFO:     Started server process [22268]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:3000 (Press CTRL+C to quit)
INFO:     Generation usage: prompt_tokens=978 completion_tokens=306 cost_usd=0.0008808
INFO:     127.0.0.1:64905 - "POST /api/generate HTTP/1.1" 200 OK

```

## Test 2 Content-Quality Review

- HTTP/client time: 7.23 seconds. Reported provider cost: USD 0.0008808.
- Card 1 evidence: exact match to the git add sentence in notes.md.
- Card 1 answer is consistent with the described staging workflow. However, the
  correction says "git add is necessary ... before git commit", again presenting
  a workflow as a universal requirement. The notes do not establish that every
  commit needs a new git add invocation. The broad misconception is consequently
  not safely corrected as written.
- Card 2 evidence: exact match to the git status sentence in notes.md.
- Card 2 application says "saving them permanently", unsupported by the notes.
  Its answer adds "staged and unstaged changes", which may be correct Git behavior
  but is not explicitly supplied in these notes. Its correction's claim that status
  does not save changes is consistent with the intended distinction, but is not
  explicitly stated in the quoted source. Under the strict notes-only rule, this
  should be treated as an inference rather than an explicit source fact.
- Outcome: live end-to-end and schema validation succeeded; content grounding is
  still imperfect. The prompt improvement did not eliminate these problems.
  Because both model and prompt differ from test 1, the two runs alone cannot
  isolate the effect of the prompt change or establish a model-quality ranking.
- Original generated output above is preserved without corrections. No paid retry
  or additional generation was performed.
