#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
# Shared zsh configuration generated for cross-machine reuse.
# Put machine-specific overrides in ~/.zshrc.local.

export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="amuse-yx"
plugins=(
  git
)

if [ -s "$ZSH/oh-my-zsh.sh" ]; then
  source "$ZSH/oh-my-zsh.sh"
fi

if [ -f "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" ]; then
  source "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
fi

if [ -f "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]; then
  source "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
fi

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
if command -v fzf >/dev/null 2>&1; then
  source <(fzf --zsh)
fi

export PATH="$HOME/.local/bin:$HOME/.pixi/bin:$HOME/.fzf/bin:$PATH"

if [ -f "$HOME/.config/dev-bootstrap/bash_aliases.sh" ]; then
  source "$HOME/.config/dev-bootstrap/bash_aliases.sh"
fi

if [ -f "$HOME/.zshrc.local" ]; then
  source "$HOME/.zshrc.local"
fi
EOF
