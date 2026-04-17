---
name: session-distiller
description: "Automatically extracts, summarizes, and distills the current session context into a minimal, token-efficient 'Context Checkpoint'. Used to pass essential state to subagents or to restart a session without losing momentum. Solves the context-bloat problem by filtering noise and focusing on the 'What, Why, and What's Next'."
---

# Session Distiller: Context Compaction for Subagents

A skill for generating high-density, low-token context handoffs. Instead of passing massive histories to subagents, the Distiller extracts only the "Critical Path" information.

## The Problem
- **Context Bloat**: Long sessions waste tokens and confuse models.
- **Subagent Fog**: Spawning a subagent with too little context leads to "I don't know where we are" responses.
- **Manual Overhead**: Manually summarizing work for a subagent is tedious and prone to missing details.

## The Solution: The "Checkpoint" Pattern
The Distiller creates a **Context Checkpoint** with four key sections:
1. **Goal**: The high-level mission.
2. **State of Play**: What is already done, where the code lives, what tools are active.
3. **The Distillation**: Key insights, decisions made, and technical constraints discovered.
4. **Subtask Specifics**: Exactly what the subagent needs to do NOW.

## Usage

### Pattern 1: Subagent Handoff (The most common use case)

When you need to spawn a worker to do a specific task:

```
1. Tell the Distiller: "Distill our progress on [Task X] for a subagent."
2. The Distiller outputs a "Context Checkpoint".
3. Use that output as the 'message' for spawn_agent.
```

### Pattern 2: Session "Save Point"

When a session gets too long and you want to "restart" or "compact" the current context:

```
1. Run session-distiller.
2. Store the output in a memory: write_memory(memory_name="project/checkpoint-v1", content=distillation).
3. In a new session/agent, read that memory to resume instantly.
```

## Distillation Modes

### `focused` (Default)
- Targets a specific sub-task.
- Includes only files and symbols relevant to that task.
- Best for: `spawn_agent` for a worker.

### `comprehensive`
- Summarizes the entire project state.
- Includes architectural decisions, known bugs, and full roadmap.
- Best for: Project handovers or session restarts.

### `minimal`
- Only the absolute essentials (3-4 bullet points).
- Best for: Very simple tasks where token count is critical.

## Integration with spawn_agent

```python
# Example of using the distilled context
distillation = """
## Context Checkpoint
Goal: Implement auth middleware.
State: Database schema is ready in /models/user.js.
Task: Create /middleware/auth.js with JWT verification.
"""

spawn_agent(
    model="gemini-3-flash-preview",
    message=f"You are a worker agent. Here is your context: {distillation}. Proceed with the Task."
)
```

## When to Distill
- Before spawning any subagent (`spawn_agent`).
- When the context window is getting full (performance degradation).
- After completing a major milestone.
- When switching from "Research/Exploration" to "Implementation".
