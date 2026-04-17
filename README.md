# Koompi Elite Agent Bundle 🚀

A one-click installer for the Koompi AI Agent Workflow. This bundle equips your AI coding agents with parallel execution, adversarial self-critique, long-term memory, and surgical boundaries.

## Installation

Run this in your terminal:

\`\`\`bash
git clone https://github.com/hangsiahong/koompi-agent-bundle.git
cd koompi-agent-bundle
./setup.sh
\`\`\`

## What is included?

1. **Global `AGENTS.md`**: The orchestrator system prompt that forces GLM-5.1 to act as a manager and delegate tasks to Gemini workers.
2. **Parallel Agent Dispatch**: Integrated `tmux` workflow for spawning multiple background agents.
3. **Session Distiller**: Context-compaction tool to prevent subagent bloat.
4. **Self-Critic**: Adversarial background reviewer.
5. **Memory Maker**: Long-term architectural sync tool.
6. **Blast Radius Check**: Pre-flight dependency mapper.

## For Maintainers (How to update this bundle)
Do not edit the skills in this repository directly. This is a compiled distribution. 
To update, use the `build-bundle.sh` script in your local development environment to compile the scattered skills into this repo.
