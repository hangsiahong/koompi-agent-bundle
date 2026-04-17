---
name: tmux-workflow
description: Use when running multiple parallel agents, monitoring long-running background tasks, or requiring a multi-pane observability dashboard for parallel implementation plans.
---

# tmux Workflow

## Overview
A tmux-based Command Center for managing parallel agent execution, background observability, and **automatic code indexing**.

## When to Use
- Implementing plans with 2+ parallel sub-agents (via dispatching-parallel-agents)
- Monitoring logs and tests simultaneously while coding
- Managing long-running background tasks (dev servers, scrapers)
- Starting a session and wanting the code index kept up to date automatically

## Core Pattern: The Command Center
- **Pane 0 (Main)**: Orchestrator / Brainstorming
- **Pane 1 (Monitor)**: Logs / Live Output / **Auto-Indexer**
- **Pane 2+ (Workers)**: Parallel sub-agent execution contexts

## Usage

### 1. Initialize Dashboard (with auto-indexing)
```bash
bash scripts/tmux-manager.sh init "ProjectName" "/path/to/project" --auto-index
```
The `--auto-index` flag automatically starts the code indexer in the Monitor pane. It will clean orphans, index new/changed files, and show status — all hands-free.

### 2. Initialize Dashboard (manual)
```bash
bash scripts/tmux-manager.sh init "ProjectName" "/path/to/project"
```

### 3. Re-index in Monitor Pane
```bash
bash scripts/tmux-manager.sh reindex "ProjectName" "/path/to/project"
```
Sends the auto-index command to Pane 1. Use this after major code changes during a session.

### 4. Check Index Status
```bash
bash scripts/tmux-manager.sh status "ProjectName" "/path/to/project"
```
Shows tracked file count, new/changed/deleted counts, and DB size — without starting a full index.

### 5. Add Worker Pane
```bash
bash scripts/tmux-manager.sh add-worker "ProjectName" "Worker Name"
```

## Integration with code-intelligence

The tmux workflow is tightly integrated with the `code-intelligence` skill:
- **Init with `--auto-index`**: Automatically keeps the LanceDB index fresh
- **`reindex` command**: Trigger re-indexing from any point in the session
- **`status` command**: Quick health check without leaving tmux

The indexer tracks file changes via mtime fingerprints, so re-indexing only processes what actually changed — fast and cheap.

## Implementation Details
The `tmux-manager.sh` script handles session naming, pane splitting, layout optimization (usually tiled or main-vertical), and delegates to the code-intelligence indexer for all indexing operations.
