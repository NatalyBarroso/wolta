---
name: git-commit-push
description: >-
  Creates the necessary commits with prefix(vX.Y.Z): description and pushes
  them to the active working branch. Use when the user asks to commit, push,
  commit and push, or prepare the upgrade-v0.2.0 commit structure.
---

# git-commit-push

Create the commits this change needs, using the project message format, then push them to the **active working branch**. Do not create a new branch unless the user asks.

## Before anything else

1. Confirm the repo root and the current branch (`git status -sb`, `git log -8 --oneline`).
2. Check `.gitignore` and the working tree. Do not stage secrets, credentials, `.env*`, `*.pem`, `credentials.json`, `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, local vaults, or backups. If a publishable pattern is missing from `.gitignore`, add it in a dedicated `chore(...)` commit **before** the feature commits.
3. Inspect `git status`, `git diff`, and `git log` in parallel. Never update git config. Never use `git add -i` / `git rebase -i`.

## Message format

```
prefix(vX.Y.Z): description
```

- `prefix` is a conventional type: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.
- `vX.Y.Z` is the **target version of the change** (today: `v0.2.0`). Read it from the upgrade plan or the intended `__version__`, not from the CLI version still on disk if that version has not been bumped yet.
- `description` is one imperative line, lowercase, no trailing period. It says why the commit exists, not a file list.

**Examples:**

```
feat(v0.2.0): generate HUMAN/SYSTEM vault layout on init
feat(v0.2.0): add reversible move engine for structural upgrades
fix(v0.2.0): keep CLI output encodable on Windows pipes
```

## How many commits

Split by **layer**, not by file count. A commit must stand alone: checking it out must leave the tree importable.

Typical slices for this upgrade:

1. `feat(vX.Y.Z):` layout / `init` / generated tree
2. `feat(vX.Y.Z):` reversible move engine / migration runner
3. `fix(vX.Y.Z):` unrelated bugfixes (console encoding, and similar)

If a file belongs to two slices (for example `init.py` changing both layout and `echo()`), write an intermediate version so each commit compiles. Do not put the later slice's dependency into an earlier commit.

If the split is obvious and the user already said to commit, execute. If the split is ambiguous, **propose the commit list first** and wait.

## Commit, then push

1. Stage only the files for the current slice. Review the staged diff.
2. Commit with a HEREDOC / PowerShell here-string. Subject is the `prefix(vX.Y.Z):` line; the body is 1–2 sentences on why.
3. Repeat until the working tree is clean of the intended changes.
4. Push the existing commits on the **current branch** to its upstream. If there is no upstream: `git push -u origin HEAD`.
5. Do not stage, unstage, or create extra commits as part of the push.
6. Do not force-push, `--no-verify`, or amend a commit that is already on the remote unless the user explicitly asks.

On Windows PowerShell:

```powershell
git commit -m @"
feat(v0.2.0): generate HUMAN/SYSTEM vault layout on init

A new vault is born with the two-space tree.
"@
```

## After

Report: branch name, commit hashes and subjects, whether the push created or updated the remote branch, and that the working tree is clean (or what was left unstaged on purpose).
