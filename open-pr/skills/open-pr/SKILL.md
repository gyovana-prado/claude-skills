---
name: open-pr
description: >
  Open a pull request end-to-end: audits staged files for sensitive/confidential data,
  formats code, commits uncommitted changes with a conventional commit message, generates
  a structured PR description, and creates the PR on GitHub. Use when the user asks to
  open, create, submit, or push a pull request.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

You are running the `open-pr` skill. Your job is to guide the user through a safe, complete pull request opening flow.

Current branch: !`git branch --show-current`

Staged files: !`git diff --cached --name-only 2>/dev/null || echo "(none)"`

Unstaged changes: !`git diff --name-only 2>/dev/null || echo "(none)"`

Follow the steps below in order. Pause and ask the user only when a step requires explicit confirmation (security risks, destructive actions). For routine steps, proceed automatically and report what you did.

---

## Step 1 — Branch Check

Check if the current branch is `main` or `master`.

- If yes: stop and tell the user they should open the PR from a feature branch. Suggest creating one: `git checkout -b <branch-name>`. Do not proceed until they switch.
- If no: continue.

---

## Step 2 — Security Audit

Read `${CLAUDE_SKILL_DIR}/security-patterns.md` to load the patterns.

**2a. Filename audit**

Check all staged and unstaged files against the sensitive filename patterns. For each match, verify whether the file is covered by `.gitignore`.

- If a sensitive file is NOT in `.gitignore`: flag it as **Medium** risk. Show the filename and ask the user if they want to add it to `.gitignore` before continuing.

**2b. Content audit**

For each text file in the staged changes, scan its content against the sensitive content patterns. Apply the false positive heuristics to avoid noise.

- **High risk finding**: pause immediately. Show the file path, the matched line (redact the value after the first 6 chars), and the pattern that matched. Ask the user explicitly: "Do you want to proceed anyway, or fix this first?"
- **Medium risk finding**: warn the user and ask.
- **Low risk finding**: mention briefly in a summary at the end of this step, then continue.

If no findings: state "No sensitive data detected." and continue.

---

## Step 3 — Code Formatting

Detect the project stack by checking for config files in the repo root:

| Config file | Stack | Formatter command |
|---|---|---|
| `go.mod` | Go | `go fmt ./...` |
| `Cargo.toml` | Rust | `cargo fmt` |
| `pyproject.toml` / `setup.py` | Python | `uv run ruff format .` (prefer ruff; fall back to `uv run black .`) |
| `package.json` with prettier | JS/TS | `npx prettier --write .` |
| `package.json` with biome | JS/TS | `npx biome format --write .` |
| `.swift-format` or `Package.swift` | Swift | `swift-format -r -i .` |

Run the appropriate formatter. If the formatter is not installed or fails, skip and mention it to the user.

After formatting, stage any new changes produced by the formatter: `git add -u`.

---

## Step 4 — Commit Uncommitted Changes

Check for uncommitted changes: `git status --short`.

If there are staged or unstaged changes:

1. Run `git diff HEAD` to understand all pending changes.
2. Generate a commit message following the **Conventional Commits** format:
   - Type: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `perf`
   - Scope (optional): the main module or area affected
   - Subject: imperative, lowercase, no period at end
   - Body (optional): bullet list of notable changes if more than one concern
3. Stage all changes: `git add -A`
4. Commit: `git commit -m "<generated message>"`
5. Report the commit message used.

If there is nothing to commit: note it and continue.

---

## Step 5 — Analyze Diff

Determine the base branch:

```bash
git remote show origin 2>/dev/null | grep "HEAD branch" | awk '{print $NF}'
```

Fall back to `main` if the command fails.

Run `git diff <base>...HEAD` and `git log <base>...HEAD --oneline` to understand all changes between the current branch and the base.

Summarize internally (do not print the full diff to the user):
- What files changed and how many
- The nature of the changes (new feature, bug fix, refactor, etc.)
- Any notable patterns across commits

---

## Step 6 — Issue Tracker Detection (Optional)

Extract a ticket identifier from the branch name using these patterns:

| Pattern | Tracker |
|---|---|
| `[A-Z]+-\d+` (e.g., `SUP-123`, `PROJ-42`) | Linear or Jira |
| `#\d+` or `gh-\d+` | GitHub Issues |
| No match | None detected |

If an identifier is found:
- For **Linear**: try `mcp__claude_ai_Linear__get_issue` if the Linear MCP is connected. If not connected, note it and skip.
- For **Jira**: try the Jira MCP if connected. If not, skip.
- For **GitHub Issues**: run `gh issue view <number>` to fetch title and description.
- If nothing is available: ask the user "Is there an issue or card associated with this work? If so, share the link or paste the description."

If a card is found, extract: **title**, **description**, and **acceptance criteria**. Check that the diff aligns with the acceptance criteria. If there is a meaningful divergence, flag it to the user before continuing.

---

## Step 7 — Generate PR Description

Using the diff summary from Step 5 and the card context from Step 6 (if available), generate a PR description with this structure:

```
## Why

<Explain the motivation. Why does this change need to go to production? What problem does it solve?>

## What

<Describe the changes and their impact. Be concrete — mention key files, new behaviors, removed code, updated APIs.>

## Validation

<If tests were added or modified: name them and describe what they cover.>
<If no tests: describe the manual validation performed or how to test this change.>
```

If a Linear/Jira/GitHub card was found, append a reference line:
```
Closes <tracker-url-or-identifier>
```

Show the generated title and description to the user for review. Allow them to edit or approve.

---

## Step 8 — Push and Open PR

After the user approves the description:

1. Push the branch: `git push -u origin HEAD`
2. Create the PR:
   ```bash
   gh pr create --title "<title>" --body "<description>"
   ```
3. Open the PR in the browser: `gh pr view --web`
4. Report the PR URL to the user.

If `gh` is not installed or not authenticated, show the user the title and body so they can open the PR manually, and explain how to install/authenticate `gh`.
