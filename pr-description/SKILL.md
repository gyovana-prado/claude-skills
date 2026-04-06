---
name: pr-description
description: Generates standardized pull request descriptions by analyzing the diff between the current branch and the main branch.
---

## Overview

This skill generates PR descriptions following a standardized format. It analyzes the changes between the current branch and the main branch to produce a description covering: **why** the change is needed, **what** was changed, and **how** it was validated.

## When to use

- The user asks to open a pull request
- The user asks for a PR description
- The user asks for a pull request description
- The user says "create a pull request description for me" or similar

## PR description format

Every PR description MUST include these three sections:

1. **Why**: Explain the motivation for the change — why this code should go to production.
2. **What**: Describe the changes made and their impact on the project.
3. **Validation**:
   - If tests were added or modified, describe which tests cover the changes.
   - If no tests were added, describe the manual validation process used.

## Dependencies

This skill requires the **Linear MCP** to query Linear cards. Use the following MCP tools:

- `mcp__claude_ai_Linear__get_issue`: Fetch a specific card by identifier (e.g., `SUP-123`).
- `mcp__claude_ai_Linear__list_issues`: Search for issues when the identifier is not obvious from the branch name.

## Execution flow

Follow these steps in order:

1. **Check branch**: Verify the user is NOT on the `main` branch. If they are, ask them to switch to a feature branch before proceeding.
2. **Analyze diff**: Run `git diff main...HEAD` to understand all changes between the current branch and main.
3. **Check for Linear card**:
   - Extract the ticket identifier from the branch name (e.g., `feature/SUP-123-add-auth` → `SUP-123`).
   - If no identifier is found, ask the user if there is a Linear card associated with this work.
   - If a card exists, fetch it via the Linear MCP and extract: **title**, **description**, and **acceptance criteria**.
   - **Validate alignment**: Compare the card's description and acceptance criteria against the actual code changes from the diff. If the implementation diverges from what the card describes, flag the discrepancy to the user before proceeding.
   - Include the Linear card reference (identifier + title) in the PR description.
4. **Commit if needed**: If there are uncommitted changes, ask the user if they want to commit before opening the PR. Do not commit automatically without confirmation.
5. **Open the PR**: Create the pull request on GitHub following the description format defined above, including the Linear card link if available.