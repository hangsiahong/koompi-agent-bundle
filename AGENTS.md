# Elite Superpowers Workflow: Koompi Edition

Follow this integrated workflow for all development tasks to ensure isolation, observability, precision, and deep code intelligence.

## 1. Planning Phase (High-Reasoning)
- **Model**: Always use **glm-5.1** in the main session for brainstorming and strategy.
- **Intelligence**: Use the `code-intelligence` skill (LanceDB) to search the codebase.
- **Pre-Flight**: Use the `blast-radius-check` skill before proposing changes to core utilities or shared functions to map out all downstream impacts.

## 2. Setup Phase (Isolation & Observability)
- **Isolation**: Use `using-git-worktrees` to create a clean directory.
- **Dashboard**: Initialize a `tmux-workflow` session:
  ```bash
  bash ~/.codex/superpowers/skills/tmux-workflow/scripts/tmux-manager.sh init "Project" "/path" --auto-index
  ```
  - **Pane 0**: Orchestrator (Main - GLM-5.1)
  - **Pane 1**: Monitor (Auto-Indexer + Logs)

## 3. Execution Phase (Parallel Workers)
**Stop trying to do everything yourself.** If a plan has 2+ independent tasks, **delegate** to parallel workers (Gemini-3-Flash) using `spawn_agent`.

### The Parallel Pattern:
1. **Distill Context**: ALWAYS run `session-distiller` first. Generate a Context Checkpoint defining Scope & Anti-Goals.
2. **Prepare Pane**: 
   ```bash
   bash ~/.codex/superpowers/skills/tmux-workflow/scripts/tmux-manager.sh add-worker "worker-1" "Task Name"
   ```
3. **Spawn Agent**: Use `spawn_agent` with role `worker` and model `gemini-3-flash-preview`. Pass the Context Checkpoint in the message.
4. **Instruct Agent to Log**: Tell the worker: 
   *"Log your progress using: bash ~/.codex/superpowers/skills/dispatching-parallel-agents/scripts/worker-log.sh worker-1 progress 'Done with X'"*
5. **Quality Control**: Use the `self-critic` skill to spawn a background adversarial agent to review the work as it happens.

### Observability:
- Watch the tmux panes to see real-time progress from all workers simultaneously.
- Use `reindex` if you need to refresh the semantic search index after workers finish.

## 4. Code Intelligence Commands
| Command | Purpose |
|---------|---------|
| `--auto PATH` | Clean orphans -> Index new/changed -> Show status |
| `--status` | Check if re-index is needed (tracked/new/changed counts) |
| `--search QUERY` | Semantic search across the codebase |

## 5. Verification & Persistence Phase
- Run the full test suite in the `Monitor` pane.
- Use `verification-before-completion` before merging.
- **Persist Knowledge**: Run the `memory-maker` skill to save any new architectural decisions, gotchas, or framework quirks discovered during the session.

---
**Core Principle**: The brain (GLM-5.1) stays in the main pane; the hands (Gemini-3-Flash) work in parallel panes. The boundaries are enforced by `session-distiller` and `blast-radius-check`. Long-term knowledge is preserved by `memory-maker`.
