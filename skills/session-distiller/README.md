# Session Distiller 🧬

A skill to solve "Context Bloat" and "Subagent Fog". It distills long conversations into high-density, token-efficient checkpoints, strongly influenced by the **Karpathy Guidelines** for surgical precision and the **Self-Critic** mentality for surfacing risks.

## Installation

```bash
# Clone into your skills directory
gh repo clone hangsiahong/session-distiller
```

## Quick Start

1. **Ask for a distillation**: "Distill our session for a subagent that will fix the CSS."
2. **Copy the output**.
3. **Spawn a subagent**: Use the distilled output as the prompt for `spawn_agent`.

## Why use this?

Standard AI history is full of tool outputs, mistakes, and repetitive thoughts. **Session Distiller** filters the noise so your subagents (and you) can focus on the signal. 

Furthermore, simply telling a subagent "do X" often leads to them over-engineering or touching unrelated files. The Distiller explicitly defines **Scope & Anti-Goals** (following Karpathy Guidelines) to keep subagents tightly focused.

## Features

- **Subagent Handoff**: Tailored, strictly scoped context for workers.
- **Session Restart**: Save state to a memory and resume later.
- **Surgical Bounds**: Explicitly tells subagents what *not* to touch.
- **Risk Surfacing**: Highlights assumptions and risks before the subagent starts working.
- **Token Optimization**: Fits complex state into <500 tokens.

Built by [hangsiahong](https://github.com/hangsiahong).
