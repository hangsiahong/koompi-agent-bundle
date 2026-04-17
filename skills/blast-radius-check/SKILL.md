---
name: blast-radius-check
description: Use before modifying shared functions, core utilities, class definitions, or database schemas. Maps out all dependencies and referencing symbols to prevent unintended breakage in other files.
---

# Blast Radius Check

A strict pre-flight check mandated by the **Karpathy Guidelines** ("Surgical Changes"). Before you change the behavior or signature of an existing symbol, you must know exactly what else will explode if you get it wrong.

## When to use this skill
- Before changing the arguments or return type of a function/method.
- Before refactoring a shared utility.
- Before modifying a database model or schema.
- When deleting seemingly "dead" code.

## The Protocol

### 1. Locate the Target
Identify the exact symbol you are about to change. Use `find_symbol` if needed to get its exact `name_path`.

### 2. Map the Radius
Run a comprehensive search for all code that depends on this symbol.
- Use the **`mcp__serena__find_referencing_symbols`** tool to get all structural references.
- If it's an API route, string constant, or dynamic event, use **`mcp__serena__search_for_pattern`** to catch loose text references.

### 3. Document the Impact
Before writing any code, list the affected files. If you are delegating to a subagent via `session-distiller`, this list MUST be included in the `⚠️ Assumptions, Risks & Blockers` section of the Context Checkpoint.

**Example Checkpoint Addition:**
```markdown
### ⚠️ Assumptions, Risks & Blockers
- **Blast Radius**: Modifying `verifyToken()` will impact:
  - `src/middleware/auth.ts`
  - `src/routes/userProfile.ts`
  - `src/services/paymentService.ts`
- **Constraint**: You MUST update all 3 files in the same commit to prevent build failures.
```

## Anti-Patterns (What NOT to do)
- ❌ Guessing: "I think this is only used in this one file."
- ❌ Blindly trusting the IDE: Forgetting to check if a frontend component depends on the backend payload structure.
- ❌ Changing the core function and leaving the downstream updates "for later."
