#!/usr/bin/env bash
set -euo pipefail

mode="user"
dry_run=0
target=""

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --mode)
      mode="${2:?missing mode}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      target="$1"
      shift
      ;;
  esac
done

if [[ -z "$target" ]]; then
  echo "Usage: $0 [--mode user|sudo] [--dry-run] [user@]host" >&2
  exit 1
fi

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

"$skill_dir/scripts/render_safe_zshrc.sh" > "$tmp_dir/.zshrc"
cp "$skill_dir/assets/tmux.conf" "$tmp_dir/.tmux.conf"
cp "$skill_dir/assets/bash_aliases.sh" "$tmp_dir/bash_aliases.sh"
cp "$skill_dir/assets/amuse-yx.zsh-theme" "$tmp_dir/amuse-yx.zsh-theme"

if [[ -d "$HOME/.oh-my-zsh" ]]; then
  tar -C "$HOME" -czf "$tmp_dir/oh-my-zsh.tgz" .oh-my-zsh
fi

if [[ -d "$HOME/.fzf" ]]; then
  tar -C "$HOME" -czf "$tmp_dir/fzf.tgz" .fzf
fi

if [[ -f "$HOME/install_pixi.sh" ]]; then
  cp "$HOME/install_pixi.sh" "$tmp_dir/install_pixi.sh"
fi

if [[ -x "$HOME/.pixi/bin/pixi" ]]; then
  mkdir -p "$tmp_dir/.pixi/bin"
  cp "$HOME/.pixi/bin/pixi" "$tmp_dir/.pixi/bin/pixi"
fi

git_user_name="$(git config --global --get user.name || true)"
git_user_email="$(git config --global --get user.email || true)"
cat >"$tmp_dir/.gitconfig" <<EOF
[user]
	name = ${git_user_name}
	email = ${git_user_email}
[column]
	ui = auto
[branch]
	sort = -committerdate
[diff]
	algorithm = histogram
	colorMoved = plain
[push]
	autoSetupRemote = true
	followTags = true
[fetch]
	prune = true
	pruneTags = true
EOF

remote_cmd='
set -e
mkdir -p "$HOME/.config/dev-bootstrap"
mkdir -p "$HOME/.bootstrap-backups"
mkdir -p "$HOME/.pixi/bin"
if [ -f "$HOME/.zshrc" ]; then cp "$HOME/.zshrc" "$HOME/.bootstrap-backups/.zshrc.$(date +%Y%m%d%H%M%S)"; fi
if [ -f "$HOME/.tmux.conf" ]; then cp "$HOME/.tmux.conf" "$HOME/.bootstrap-backups/.tmux.conf.$(date +%Y%m%d%H%M%S)"; fi
if [ -f "$HOME/.gitconfig" ]; then cp "$HOME/.gitconfig" "$HOME/.bootstrap-backups/.gitconfig.$(date +%Y%m%d%H%M%S)"; fi
cp "$HOME/.bootstrap-stage/.tmux.conf" "$HOME/.tmux.conf"
cp "$HOME/.bootstrap-stage/bash_aliases.sh" "$HOME/.config/dev-bootstrap/bash_aliases.sh"
cp "$HOME/.bootstrap-stage/.gitconfig" "$HOME/.gitconfig"
if command -v zsh >/dev/null 2>&1; then
  if [ ! -d "$HOME/.oh-my-zsh" ]; then
    if [ -f "$HOME/.bootstrap-stage/oh-my-zsh.tgz" ]; then
      tar -xzf "$HOME/.bootstrap-stage/oh-my-zsh.tgz" -C "$HOME"
    elif command -v curl >/dev/null 2>&1; then
      RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    elif command -v wget >/dev/null 2>&1; then
      RUNZSH=no CHSH=no sh -c "$(wget -qO- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    fi
  fi
  cp "$HOME/.bootstrap-stage/.zshrc" "$HOME/.zshrc"
  mkdir -p "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins"
  if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" ]; then
    git clone --depth 1 https://github.com/zsh-users/zsh-autosuggestions "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions"
  fi
  if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ]; then
    git clone --depth 1 https://github.com/zsh-users/zsh-syntax-highlighting.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting"
  fi
  mkdir -p "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes"
  cp "$HOME/.bootstrap-stage/amuse-yx.zsh-theme" "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/amuse-yx.zsh-theme"
else
  cp "$HOME/.bootstrap-stage/.zshrc" "$HOME/.zshrc.bootstrap"
  echo "zsh missing: wrote $HOME/.zshrc.bootstrap instead of activating ~/.zshrc"
fi
'

fzf_cmd='
if command -v fzf >/dev/null 2>&1; then
  echo "fzf already installed"
elif [ -f "$HOME/.bootstrap-stage/fzf.tgz" ] && [ ! -d "$HOME/.fzf" ]; then
  tar -xzf "$HOME/.bootstrap-stage/fzf.tgz" -C "$HOME"
  "$HOME/.fzf/install" --all --no-update-rc || true
elif [ -d "$HOME/.fzf" ]; then
  "$HOME/.fzf/install" --all --no-update-rc || true
elif command -v git >/dev/null 2>&1; then
  git clone --depth 1 https://github.com/junegunn/fzf.git "$HOME/.fzf"
  "$HOME/.fzf/install" --all --no-update-rc
else
  echo "Skipping fzf install: missing git"
fi
'

pixi_cmd='
if command -v pixi >/dev/null 2>&1; then
  echo "pixi already installed"
elif [ -x "$HOME/.bootstrap-stage/.pixi/bin/pixi" ]; then
  mkdir -p "$HOME/.pixi/bin"
  cp "$HOME/.bootstrap-stage/.pixi/bin/pixi" "$HOME/.pixi/bin/pixi"
  chmod +x "$HOME/.pixi/bin/pixi"
elif [ -f "$HOME/.bootstrap-stage/install_pixi.sh" ]; then
  if command -v timeout >/dev/null 2>&1; then
    timeout 120s bash "$HOME/.bootstrap-stage/install_pixi.sh" || echo "Skipping pixi install after timeout or download failure"
  else
    bash "$HOME/.bootstrap-stage/install_pixi.sh" || echo "Skipping pixi install after download failure"
  fi
elif command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1; then
  if command -v timeout >/dev/null 2>&1; then
    timeout 120s bash -lc '"'"'"'"'"'"'"'"'curl -fsSL https://pixi.sh/install.sh | bash || wget -qO- https://pixi.sh/install.sh | bash'"'"'"'"'"'"'"'"' || echo "Skipping pixi install after timeout or download failure"
  else
    bash -lc '"'"'"'"'"'"'"'"'curl -fsSL https://pixi.sh/install.sh | bash || wget -qO- https://pixi.sh/install.sh | bash'"'"'"'"'"'"'"'"' || echo "Skipping pixi install after download failure"
  fi
else
  echo "Skipping pixi install: missing curl and wget"
fi
'

sudo_cmd='
if command -v sudo >/dev/null 2>&1; then
  if command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y zsh tmux git ripgrep
  elif command -v apt >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y zsh tmux git ripgrep
  fi
  if command -v zsh >/dev/null 2>&1; then
    chsh -s "$(command -v zsh)" || true
  fi
fi
'

if [[ "$dry_run" -eq 1 ]]; then
  echo "__DRY_RUN__"
  echo "target: $target"
  echo "mode: $mode"
  echo "stage files: .zshrc, .tmux.conf, bash_aliases.sh, amuse-yx.zsh-theme"
  echo "remote actions: backup dotfiles, install shared files, install pixi, optionally install system packages"
  exit 0
fi

ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" 'rm -rf "$HOME/.bootstrap-stage" && mkdir -p "$HOME/.bootstrap-stage"'
stage_files=("$tmp_dir/.zshrc" "$tmp_dir/.tmux.conf" "$tmp_dir/bash_aliases.sh" "$tmp_dir/amuse-yx.zsh-theme" "$tmp_dir/.gitconfig")
if [[ -f "$tmp_dir/oh-my-zsh.tgz" ]]; then
  stage_files+=("$tmp_dir/oh-my-zsh.tgz")
fi
if [[ -f "$tmp_dir/fzf.tgz" ]]; then
  stage_files+=("$tmp_dir/fzf.tgz")
fi
if [[ -f "$tmp_dir/install_pixi.sh" ]]; then
  stage_files+=("$tmp_dir/install_pixi.sh")
fi
scp -q "${stage_files[@]}" "$target:~/.bootstrap-stage/"
if [[ -x "$tmp_dir/.pixi/bin/pixi" ]]; then
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" 'mkdir -p "$HOME/.bootstrap-stage/.pixi/bin"'
  scp -q "$tmp_dir/.pixi/bin/pixi" "$target:~/.bootstrap-stage/.pixi/bin/pixi"
fi
ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "$remote_cmd"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "$fzf_cmd"
ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "$pixi_cmd"
if [[ "$mode" == "sudo" ]]; then
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "$sudo_cmd"
fi

"$skill_dir/scripts/inspect_host.sh" "$target"
