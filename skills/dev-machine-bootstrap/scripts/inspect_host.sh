#!/usr/bin/env bash
set -euo pipefail

target="${1:-local}"

run_local() {
  bash -lc '
    printf "__TARGET__\nlocal\n"
    printf "__HOST__\n"; hostname
    printf "__USER__\n"; whoami
    printf "__KERNEL__\n"; uname -a
    printf "__OS_RELEASE__\n"; cat /etc/os-release 2>/dev/null || true
    printf "__SHELL__\n"; getent passwd "$(whoami)" 2>/dev/null | cut -d: -f7 || printf "%s\n" "${SHELL:-unknown}"
    printf "__PKG_MANAGER__\n"
    command -v apt || command -v dnf || command -v yum || command -v pacman || command -v zypper || echo "__NO_PKG__"
    printf "__SUDO__\n"
    if command -v sudo >/dev/null 2>&1; then
      if sudo -n true >/dev/null 2>&1; then
        echo "NOPASSWD"
      else
        echo "NEEDS_PASSWORD"
      fi
    else
      echo "MISSING"
    fi
    printf "__TOOLS__\n"
    for x in zsh fzf tmux pixi git curl wget rg fd bat eza nvim vim gcc g++ make; do
      printf "%s: " "$x"
      if command -v "$x" >/dev/null 2>&1; then
        command -v "$x"
      elif [[ "$x" == "fzf" && -x "$HOME/.fzf/bin/fzf" ]]; then
        echo "$HOME/.fzf/bin/fzf"
      elif [[ "$x" == "pixi" && -x "$HOME/.pixi/bin/pixi" ]]; then
        echo "$HOME/.pixi/bin/pixi"
      else
        echo "__MISSING__"
      fi
    done
    printf "__DOTFILES__\n"
    for f in ~/.bashrc ~/.bash_profile ~/.zshrc ~/.tmux.conf ~/.gitconfig; do
      if [ -e "$f" ]; then
        printf "present %s\n" "$f"
      else
        printf "missing %s\n" "$f"
      fi
    done
  '
}

run_remote() {
  local remote="$1"
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$remote" '
    bash -lc '"'"'
      printf "__TARGET__\nremote\n"
      printf "__HOST__\n"; hostname
      printf "__USER__\n"; whoami
      printf "__KERNEL__\n"; uname -a
      printf "__OS_RELEASE__\n"; cat /etc/os-release 2>/dev/null || true
      printf "__SHELL__\n"; getent passwd "$(whoami)" 2>/dev/null | cut -d: -f7 || printf "%s\n" "${SHELL:-unknown}"
      printf "__PKG_MANAGER__\n"
      command -v apt || command -v dnf || command -v yum || command -v pacman || command -v zypper || echo "__NO_PKG__"
      printf "__SUDO__\n"
      if command -v sudo >/dev/null 2>&1; then
        if sudo -n true >/dev/null 2>&1; then
          echo "NOPASSWD"
        else
          echo "NEEDS_PASSWORD"
        fi
      else
        echo "MISSING"
      fi
      printf "__TOOLS__\n"
      for x in zsh fzf tmux pixi git curl wget rg fd bat eza nvim vim gcc g++ make; do
        printf "%s: " "$x"
        if command -v "$x" >/dev/null 2>&1; then
          command -v "$x"
        elif [[ "$x" == "fzf" && -x "$HOME/.fzf/bin/fzf" ]]; then
          echo "$HOME/.fzf/bin/fzf"
        elif [[ "$x" == "pixi" && -x "$HOME/.pixi/bin/pixi" ]]; then
          echo "$HOME/.pixi/bin/pixi"
        else
          echo "__MISSING__"
        fi
      done
      printf "__DOTFILES__\n"
      for f in ~/.bashrc ~/.bash_profile ~/.zshrc ~/.tmux.conf ~/.gitconfig; do
        if [ -e "$f" ]; then
          printf "present %s\n" "$f"
        else
          printf "missing %s\n" "$f"
        fi
      done
    '"'"'
  '
}

if [[ "$target" == "local" || "$target" == "localhost" ]]; then
  run_local
else
  run_remote "$target"
fi
