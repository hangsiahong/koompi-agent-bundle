---
name: dispatching-parallel-agents
description: Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies. Integrated with tmux-workflow for observability and session-distiller for context management.
---

# Parallel Agent Dispatch (tmux-Integrated)

## Overview
Speed up development by offloading independent tasks to parallel **Worker Agents** (Gemini-3-Flash) while you (GLM-5.1) coordinate from the **Orchestrator** pane.

## The Workflow

### 1. Identify Independent Tasks
Group your implementation plan into chunks that don't touch the same files.
- Task A: `src/auth/*.ts`
- Task B: `src/models/*.ts`
- Task C: `src/routes/*.ts`

### 2. Distill Context (CRITICAL)
Before spawning agents, you MUST extract the current state so the workers aren't lost. 
Use the **Session Distiller**:
- Prompt the Distiller to create a "Context Checkpoint" for the specific task.
- Ensure the distillation defines **Scope & Anti-Goals** (what not to touch) and **Verification** steps.

### 3. Dispatch with observability
For each task, use the `spawn_agent` tool. In the `message` to the agent, pass the **Context Checkpoint** generated in Step 2, assign them a **Worker ID**, and tell them to log their progress.

**Example Dispatch Command:**
```bash
# 1. Create the pane in tmux (run this yourself)
bash ~/.codex/superpowers/skills/tmux-workflow/scripts/tmux-manager.sh add-worker "worker-1" "Auth Implementation"

# 2. Spawn the agent (use spawn_agent tool)
# Prompt: "You are a worker agent. 
# Here is your Context Checkpoint: [Paste Distilled Context Here].
# Log progress using:
# bash ~/.codex/superpowers/skills/dispatching-parallel-agents/scripts/worker-log.sh worker-1 progress 'Message'"
```

### 4. Monitor
Watch the tmux panes. Each pane tails its own log file (`/tmp/codex-logs/worker-id.log`). You'll see real-time updates as the sub-agents work.

### 5. Collect & Merge
Once agents finish, they will report back in the main session. Review their work, run tests, and commit.

## Why this works
- **GLM-5.1** is the Brain: Handles the reasoning and planning.
- **Session Distiller** is the Filter: Prevents context bloat and enforces surgical boundaries.
- **Gemini-3-Flash** is the Hands: Handles the coding and testing in parallel.
- **tmux** is the Eyes: Provides a real-time dashboard of all active workers.

## Best Practices
- **Isolation**: Ensure agents don't edit the same files at the same time.
- **Small Batches**: Give agents specific, bounded tasks.
- **Strict Scope**: Always use Distiller to give agents Anti-Goals (e.g., "Do NOT refactor the router").
