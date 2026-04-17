# 🧠 Self-Critic

An autonomous adversarial critic agent that spawns in the background to challenge, question, and find flaws in your work. Think of it as a **devil's advocate that runs on autopilot**.

## What It Does

```
Builder works → Critic reviews → Critic injects feedback → Builder improves
```

The critic spawns as a background agent with a **different model** than the builder (for perspective diversity) and provides structured critique covering:

- 🔴 **Wrong** — Things that are factually incorrect or broken
- 🟡 **Risky** — Things that might work but are dangerous or fragile
- 🟠 **Smelly** — Things that work but are bad practice or over-engineered
- 🔵 **Missing** — Important things that were overlooked
- 🟢 **Better Way** — Alternative approaches worth considering

## Harshness Levels

| Level | Description | Best For |
|-------|-------------|----------|
| `paranoid` | Maximum scrutiny. Challenges everything. | Security, finance, production |
| `reasonable` | Balanced review. Catches real issues. | Most development tasks (default) |
| `chill` | Light check. Only flags obvious mistakes. | Prototyping, exploration |

## Installation

```bash
# Clone into your Codex skills directory
git clone https://github.com/hangsiahong/self-critic.git ~/.codex/skills/self-critic
```

Or install via skill-installer:

```bash
# If using Codex skill-installer
# Point to: github.com/hangsiahong/self-critic
```

## Usage

### One-Shot Critique

After completing work, spawn a critic for a single review:

```
Use $self-critic to review my latest implementation with reasonable harshness.
```

### Continuous Background Critic

Spawn at task start and feed it updates as you work:

```
Use $self-critic in continuous mode (reasonable) to monitor my work on this feature.
```

### Dual-Critic (Maximum Coverage)

Two critics with different models:

```
Use $self-critic with dual critics (paranoid + chill) for comprehensive review.
```

## Structure

```
self-critic/
├── SKILL.md              # Core skill instructions
├── agents/
│   └── openai.yaml       # UI metadata
├── scripts/
│   └── build-critic-prompt.sh   # Generate critic prompts from templates
└── references/
    ├── paranoid.md        # Paranoid critic system prompt
    ├── reasonable.md      # Reasonable critic system prompt
    └── chill.md           # Chill critic system prompt
```

## Philosophy

Inspired by:
- **Adversarial Red Teaming** — Attack your own work before others do
- **Reflexion Pattern** — Self-improvement through critique loops
- **Rubber Duck Debugging** — The act of explaining reveals the flaws
- **Senior Engineer Code Review** — "I've seen this pattern fail before..."

## License

MIT
