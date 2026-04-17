---
name: memory-maker
description: Use at the end of a session, milestone, or when closing a branch. Permanently records architectural decisions, "gotchas", and state changes to the long-term memory system so future agents don't repeat mistakes.
---

# Memory Maker (Long-Term Architecture Sync)

While `session-distiller` handles short-term context for subagents, **Memory Maker** is for long-term project persistence. It ensures that hard-earned knowledge doesn't disappear when the conversation thread is closed.

## When to use this skill
- You just solved a very tricky bug and discovered a quirk about the codebase or framework.
- You finalized a major architectural decision (e.g., "We are using Zustand for state, not Context").
- You finished a feature branch and are about to merge.
- You encountered a recurring tool failure and found a workaround.

## The Protocol

### 1. Identify the Knowledge
Determine if the information is:
- **Project-Specific**: Rules about this specific codebase (e.g., "The user ID must be cast to string before querying Mongo").
- **Global**: Rules about a language or framework that apply everywhere (e.g., "In Next.js 14, always use `use client` at the very top").

### 2. Write the Memory
Use the **`mcp__serena__write_memory`** tool to persist the knowledge.

**Naming Convention (`memory_name`):**
- Use topics to organize. Format: `topic/subtopic/detail`
- Example: `auth/jwt/header_quirk`
- Example: `architecture/state_management`
- If the rule is global across all projects: `global/nextjs/server_actions`

**Content Format:**
```markdown
# [Topic Title]

## The Decision / Rule
[State the rule clearly. E.g., "All dates must be stored as UTC ISO strings."]

## Why (The Context)
[Explain the reasoning or the bug that caused this rule.]

## Example
[Provide a quick code snippet of the right way and wrong way.]
```

### 3. Update Project Documentation (Optional but Recommended)
If the knowledge represents a major shift, also update or append to `ARCHITECTURE.md` or `CONTRIBUTING.md` in the project root.

## Anti-Patterns
- ❌ Assuming the LLM will "just remember" for the next session.
- ❌ Writing bloated memories: Keep them focused on rules and constraints, not a diary of what you did today.
