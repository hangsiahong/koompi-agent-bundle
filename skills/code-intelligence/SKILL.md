---
name: code-intelligence
description: Use when working on large, multi-service codebases where semantic search and global project context are needed to find relevant code or explain architecture.
---

# Code Intelligence (LanceDB)

## Overview
A semantic search and retrieval system powered by LanceDB and KConsole Gemini Embeddings. It allows you to search your codebase by "meaning" rather than just keywords. **Tracks file changes, cleans orphans, and only re-indexes what changed.**

## When to Use
- You need to find code but don't know the exact filenames or variable names.
- Working across multiple microservices where dependencies are unclear.
- "Remembering" architecture patterns from different parts of the project.
- Before starting a task on a project that has changed since last session.

## Commands

All commands use `scripts/indexer.py`:

### Check Status
See what's indexed, what's new, changed, or deleted:
```bash
python3 scripts/indexer.py --status --project-root ./your-project
```
Returns: tracked count, new/changed/deleted files, DB size, last index time.
Exit code 0 = up to date, 1 = needs re-index.

### Smart Auto-Index (Recommended)
Clean orphans + index new/changed + show final status in one shot:
```bash
python3 scripts/indexer.py --auto ./your-project
```
This is the **default command to use**. It handles everything.

### Index Only
Index new and changed files (no cleanup):
```bash
python3 scripts/indexer.py --index ./your-project
```

### Clean Orphans
Remove chunks for files that no longer exist on disk:
```bash
python3 scripts/indexer.py --clean --project-root ./your-project
```

### Semantic Search
Search by meaning, not keywords:
```bash
python3 scripts/indexer.py --search "How is user authentication handled?" --project-root ./your-project
```

## How Tracking Works

The indexer maintains `.lancedb/.indexed_files.json` with:
- **File fingerprints** (`path:mtime`) — detects edits automatically
- **Deleted file detection** — compares tracked paths against current filesystem
- **Last index timestamp** — know when the index was last updated
- **Backward compatible** — auto-migrates v1 format to v2

Supported file types: `.py`, `.md`, `.js`, `.ts`, `.tsx`, `.jsx`, `.sh`, `.json`, `.yml`, `.yaml`, `.toml`, `.sql`, `.rs`, `.go`, `.rb`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`, `.css`, `.html`, `.svelte`, `.vue`

Automatically skips: `node_modules`, `dist`, `.git`, `__pycache__`, `.venv`, `build`, `.lancedb`, and other noise directories.

## Best Practices
- **Run `--auto` after major refactors or adding new services** — it only processes what changed.
- **Use `--status` to check before starting work** — see if the index is stale.
- **Combined with tmux-workflow**: The `tmux-manager.sh init --auto-index` flag starts indexing automatically in the monitor pane.
- **DB is portable**: The `.lancedb/` directory lives in your project root. Add it to `.gitignore`.
