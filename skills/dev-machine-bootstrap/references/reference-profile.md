# Recommended Reference Profile

Use this profile when the user wants a clean, opinionated baseline instead of copying the current machine's dotfiles. It is derived from the current working setup but removes host-specific paths, proxies, secrets, and company-network assumptions.

## Installation Policy

### Install as system packages

- `zsh`
  - Needed for the shared shell profile and daily interactive use.
- `tmux`
  - Stable, distro-packaged, and simpler to maintain at the system layer.
- `ripgrep`
  - High-value default search tool for shell and editor workflows.

### Install in user space

- `oh-my-zsh`
  - Keep in the user's home directory.
- `zsh-autosuggestions`
  - Keep under `${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/`.
- `zsh-syntax-highlighting`
  - Keep under `${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/`.
- `fzf`
  - Install under `~/.fzf` and expose `~/.fzf/bin` in `PATH`.
- `pixi`
  - Install under `~/.pixi/bin`.

### Optional tools

- `fd`
  - Add when the user prefers a modern file finder to complement `rg`.
- `bat`
  - Add when syntax-highlighted paging is useful.
- `eza`
  - Add when the user wants richer directory listings.
- `neovim`
  - Add only when the user explicitly wants editor bootstrap in scope.

## Recommended Config Layout

- `~/.zshrc`
  - Use the output of `scripts/render_safe_zshrc.sh`.
- `~/.zshrc.local`
  - Reserve for machine-specific overrides such as custom `PATH`, editor choice, private endpoints, or temporary proxies.
- `~/.tmux.conf`
  - Use `assets/tmux.conf`.
- `~/.config/dev-bootstrap/bash_aliases.sh`
  - Use `assets/bash_aliases.sh`.
- `${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/amuse-yx.zsh-theme`
  - Use `assets/amuse-yx.zsh-theme`.
- `~/.gitconfig`
  - Use a minimal identity plus safe defaults; do not copy local absolute-path settings such as `core.excludesfile`.

## Recommended Tool Configuration

### zsh

- Theme: `amuse-yx`
- Plugin model:
  - Keep `oh-my-zsh` for prompt and base shell behavior.
  - Install `zsh-autosuggestions` and `zsh-syntax-highlighting` in the user's custom plugin directory.
- PATH policy:
  - Include `$HOME/.local/bin`, `$HOME/.pixi/bin`, and `$HOME/.fzf/bin`.
  - Keep all machine-specific additions in `~/.zshrc.local`.
- Safety rule:
  - Do not place tokens, proxy exports, or infrastructure-specific endpoints in shared shell config.

### tmux

- Prefix: backtick `` ` ``
- Numbering:
  - Start windows and panes at `1`.
- Navigation:
  - Use `hjkl` pane movement and `-` / `\` pane splitting.
- Status line:
  - Keep the current minimal session/window/time layout from `assets/tmux.conf`.

### git

- Recommended minimum:
  - `user.name`
  - `user.email`
  - `push.autoSetupRemote=true`
  - `fetch.prune=true`
  - `fetch.pruneTags=true`
  - `diff.algorithm=histogram`
- Avoid in the default baseline:
  - Absolute-path `core.excludesfile`
  - Machine-specific credential helpers
  - Proxy config

### fzf

- Install via the upstream repo into `~/.fzf`.
- Run the install script with shell integration enabled and rc rewriting disabled when the shared zshrc already sources `~/.fzf.zsh`.
- Ensure `~/.fzf/bin` is in `PATH`.

### pixi

- Install into `~/.pixi/bin`.
- Keep it as a generic per-user package/workflow manager; do not hardcode project-specific pixi configuration into the base skill.

### ripgrep

- No custom baseline config required.
- Treat it as the default search primitive in shell workflows and in future setup scripts.

## Default Bootstrap Recipe

1. Install system packages: `zsh`, `tmux`, `ripgrep`.
2. Install user-space tools: `oh-my-zsh`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `fzf`, `pixi`.
3. Copy the shared theme, tmux config, aliases file, and generated zshrc.
4. Write a minimal `~/.gitconfig`.
5. Leave `~/.zshrc.local` empty for future host-specific additions.

## What This Profile Intentionally Omits

- Proxy aliases
- API keys and tokens
- Company-specific no-proxy rules
- Local toolchain paths under `/opt` or another workstation's home directory
- Editor bootstrap beyond a minimal shell-first environment
