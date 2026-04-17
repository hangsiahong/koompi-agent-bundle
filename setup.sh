#!/bin/bash
# Koompi Elite Agent Bundle Installer

echo "🚀 Installing Koompi Agent Bundle..."

# 1. Setup global AGENTS.md
mkdir -p ~/.codex
cp ./AGENTS.md ~/.codex/AGENTS.md
echo "✅ Installed global AGENTS.md"

# 2. Setup Superpowers
mkdir -p ~/.codex/superpowers/skills
cp -r ./skills/* ~/.codex/superpowers/skills/
echo "✅ Installed all Agent Skills"

# 3. Setup global hooks
echo "export SELF_CRITIC_LEVEL=reasonable" >> ~/.bashrc
echo "export TMUX_WORKFLOW_AUTO_INDEX=true" >> ~/.bashrc

echo "🎉 Installation Complete! Please restart your terminal."
echo "   Your AI agents are now equipped with the Koompi Elite Workflow."
