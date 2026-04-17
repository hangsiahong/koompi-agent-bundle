---
name: self-critic
description: "Autonomous adversarial critic agent that spawns in the background to challenge, question, and find flaws in the builder agent's work. Use when: (1) working on complex tasks where correctness matters, (2) building features that need a second opinion, (3) writing code that could have hidden assumptions, (4) any task where you want an independent devil's advocate reviewing your reasoning and output in real-time. Spawns a background critic with configurable harshness levels (paranoid/reasonable/chill) that injects non-blocking feedback."
---

# Self-Critic: Adversarial Background Reviewer

An autonomous critic agent that watches your work and challenges it from every angle. Inspired by adversarial red-teaming and self-reflection patterns from AI research.

## How It Works

The pattern: **Builder works → Critic reviews → Critic injects feedback → Builder improves**

1. Spawn a background critic agent using `spawn_agent` with a different model for perspective diversity
2. Pass the builder's recent actions and outputs to the critic
3. Critic responds with structured critique covering logic flaws, assumptions, blind spots, and alternatives
4. Inject the critique back into the main conversation

## Harshness Levels

Control critique intensity with the `SELF_CRITIC_LEVEL` environment variable or pass it in the spawn instruction:

### `paranoid` (Maximum Scrutiny)
- Challenges everything. Assumes the builder is wrong until proven otherwise.
- Questions every assumption, every variable name, every architectural choice.
- Looks for: security holes, race conditions, off-by-one errors, edge cases, over-engineering, under-engineering.
- Best for: security-sensitive code, production deployments, financial logic.

### `reasonable` (Balanced Review) — DEFAULT
- Asks "is this the right approach?" rather than "why is everything wrong?"
- Catches real bugs and logical errors without being exhausting.
- Looks for: common bugs, missed edge cases, better alternatives, code smells.
- Best for: most development tasks.

### `chill` (Light Check)
- Only flags obvious mistakes and genuinely bad ideas.
- Offers suggestions without being pushy.
- Looks for: typos in logic, completely wrong approaches, obvious missing pieces.
- Best for: prototyping, exploration, low-stakes tasks.

## Usage Patterns

### Pattern 1: One-Shot Critique (Single Review)

After completing a significant piece of work, spawn a critic for a single review pass:

```
Use spawn_agent with:
  - model: gemini-3-flash-preview (different model for diversity)
  - role: default
  - message: |
      You are an adversarial code critic (harshness: reasonable).
      
      Review the following work and respond with structured critique:
      
      ## Context
      [Paste the task description and what was done]
      
      ## Output to Critique
      [Paste the code/output produced]
      
      ## Your Critique Format
      1. **Wrong**: Things that are factually incorrect or broken
      2. **Risky**: Things that might work but are dangerous or fragile
      3. **Smelly**: Things that work but are bad practice or over-engineered
      4. **Missing**: Important things that were overlooked
      5. **Better Way**: Alternative approaches worth considering
```

### Pattern 2: Continuous Background Critic

Spawn at the start of a task and feed it updates:

```
# Step 1: Spawn the critic at task start
critic_id = spawn_agent(
  model: "gemini-3-flash-preview",
  message: "You are a persistent adversarial critic (harshness: {level}).
            Wait for work samples to review. For each sample, provide 
            structured critique using the format in references/critic-prompts.md"
)

# Step 2: After each significant action, send work to critic
send_input(target=critic_id, message="Review this: [latest output]")

# Step 3: Check critic feedback before finalizing
wait_agent(targets=[critic_id])
```

### Pattern 3: Dual-Critic (Cross-Model Review)

Spawn two critics with different models for maximum diversity:

```
# Critic 1: Fast model, catches obvious issues
spawn_agent(model="gemini-3-flash-preview", message=critic_prompt_fast)

# Critic 2: Reasoning model, catches deep issues  
spawn_agent(model="glm-5.1", message=critic_prompt_deep)
```

## Critic Response Format

The critic always responds with this structure:

```
## Critique [harshness-level] | [timestamp]

### 🔴 Wrong
- [Things that are factually incorrect, broken, or will fail]

### 🟡 Risky  
- [Things that might work but are dangerous or fragile]

### 🟠 Smelly
- [Things that work but are bad practice or over-engineered]

### 🔵 Missing
- [Important things that were overlooked]

### 🟢 Better Way
- [Alternative approaches worth considering]

### Summary
[1-2 sentence overall assessment: sound / concerning / broken]
```

## When to Trigger the Critic

- After writing a complete function or module
- After making an architectural decision
- Before committing or creating a PR
- When you feel "this was too easy" (it probably was)
- When the task involves: security, money, data integrity, performance, concurrency
- After a long chain of tool calls without validation

## Important Notes

- **Use a DIFFERENT model** than the builder for perspective diversity. If you're GLM-5.1, use Gemini-3-Flash as critic, and vice versa.
- **Don't wait for the critic** on the critical path. Send work, continue building, check feedback later.
- **Critique is advice, not commands.** The builder decides what to act on.
- **Close the critic agent** when done to free resources: `close_agent(target=critic_id)`
