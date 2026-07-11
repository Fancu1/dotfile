---
name: local-git-review
description: Use for local Git review tasks such as reviewing a commit, branch, commit range, or preparing an isolated local checkout before code review.
---

# Local Git Review

## Overview

This skill standardizes how Claude performs local Git-based reviews.

Use it when the task is:
- review this commit
- review this branch
- review this commit range
- clone/fetch code locally for review
- inspect a PR or patch in a local Git workspace

This skill is about **collecting trustworthy local Git evidence**.  
It does **not** replace `code-review`; final findings should still follow the existing findings-first review style.

## Default Workspace Policy

1. If the current working directory is already the target repository, reuse it.
2. Otherwise, use an isolated directory under:

```bash
~/code-review-worktrees/
```

3. Prefer shared bare mirror + per-run worktree when the caller already provides that structure.
4. Do not reuse a mutable shared working tree across concurrent reviews.

## Default Flow

1. Identify the review target
- Single commit
- Branch vs base branch
- Commit range
- PR head vs base

2. Prepare local code
- Prefer `gh repo clone` for private repos
- If clone already exists, prefer `git fetch`
- Avoid full re-clone when a reusable mirror or local checkout is available

3. Reconstruct context
- Read `git log --oneline --decorate --graph --max-count 40`
- Read `git show <sha>` for commit review
- Read `git diff --stat`
- Read `git diff --find-renames <base>...<head>` or the exact range in question

4. Expand beyond the diff
- Read affected implementation files
- Read related tests
- Read relevant configuration
- Read adjacent modules, callers, callees, and error paths

5. Produce review output
- Findings first
- Ordered by severity
- Grounded in local code evidence, not only commit messages or summaries

## Required Behaviors

- Never review from commit message alone
- Never review from diff alone when related code/test/config can be read locally
- If base/head is unclear, infer it from Git state first before asking
- When the user says "review this commit", default to:
  - `git show <sha>`
  - nearby commits
  - affected modules

## Boundaries

- Default to read-only actions
- Do not `push`
- Do not `merge`
- Do not `reset --hard`
- Do not change remote state
- Do not post remote comments unless the user explicitly asked for that

## Hand-off to Code Review

After local Git evidence is collected, use the existing `code-review` expectations for:
- findings-first ordering
- severity
- risk explanation
- concrete fix direction
