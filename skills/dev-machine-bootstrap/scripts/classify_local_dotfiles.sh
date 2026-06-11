#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -eq 0 ]]; then
  set -- "$HOME/.zshrc" "$HOME/.tmux.conf" "$HOME/.gitconfig"
fi

safe_patterns='^(plugins=|ZSH_THEME=|alias [A-Za-z0-9_-]+=|source \$ZSH/oh-my-zsh\.sh|export ZSH=|set-option |set-window-option |bind |unbind |\[ -f ~/.fzf\.zsh \] && source ~/.fzf\.zsh|source <\(fzf --zsh\)|export PATH="\$HOME/\.local/bin:\$HOME/\.pixi/bin:\$PATH"|export PATH="\$HOME/\.pixi/bin:\$PATH"|export PATH="\$HOME/\.local/bin:\$PATH"|[[:space:]]*$|#)'
blocked_patterns='(API_KEY|TOKEN|SECRET|PASSWORD|AUTH|http_proxy|https_proxy|all_proxy|NO_PROXY|no_proxy|sk-[A-Za-z0-9]|AIza[0-9A-Za-z_-]+)'
parameterized_patterns='(/opt/|/home/|LD_LIBRARY_PATH|NVM_DIR|nvm\.sh|bash_completion|conda|java|go/bin|cargo/env|SSH|ssh/config|PATH=)'

for file in "$@"; do
  printf "__FILE__ %s\n" "$file"
  if [[ ! -f "$file" ]]; then
    echo "status: missing"
    continue
  fi
  echo "status: present"
  while IFS= read -r line; do
    if [[ "$line" =~ $blocked_patterns ]]; then
      printf "blocked: %s\n" "$line"
    elif [[ "$line" =~ $parameterized_patterns ]]; then
      printf "parameterized: %s\n" "$line"
    elif [[ "$line" =~ $safe_patterns ]]; then
      printf "safe: %s\n" "$line"
    else
      printf "review: %s\n" "$line"
    fi
  done <"$file"
done
