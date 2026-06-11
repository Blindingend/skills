---
name: dev-machine-bootstrap
description: Inspect local or remote Linux machines, classify reusable dotfiles, and plan or apply a safe developer-machine bootstrap. Use when Codex needs to initialize a new dev host over SSH, migrate shell/tmux/git/pixi setup with compatibility checks, audit an existing machine before setup, or extract cross-machine-safe dotfiles from a current workstation.
---

# Dev Machine Bootstrap

Inspect first. Prefer facts from the target host and current dotfiles over assumptions.

## Workflow

1. Determine the mode from the user request.
   - If the user asks to inspect, audit, survey, or research a machine, stay in `inspect`.
   - If the user asks to organize reusable config or separate safe vs machine-specific settings, run dotfile classification first.
   - If the user asks to set up or bootstrap a host, inspect first and then apply only after presenting the plan unless the user explicitly wants immediate execution.
2. Collect host facts with `scripts/inspect_host.sh`.
   - Use it for local hosts and SSH targets.
   - Capture OS, package manager, shell, sudo capability, core tools, and existing dotfiles.
3. Classify local config with `scripts/classify_local_dotfiles.sh`.
   - Treat secrets, proxies, tokens, absolute paths, and host-specific environment variables as non-default migration content.
   - Keep tmux config, generic aliases, safe git identity, and generic shell plugins as migration candidates.
   - Skip this step when the user prefers a clean baseline instead of copying from the current machine.
4. Generate or refresh safe shell config with `scripts/render_safe_zshrc.sh` when a reusable zsh profile is needed.
   - Use the generated file as the baseline.
   - Put machine-specific additions in `~/.zshrc.local` instead of hardcoding them into the shared template.
   - Copy bundled assets from `assets/` to the target host when installing a theme, tmux config, or shared aliases.
   - If the user wants a fresh machine without local migration, use the recommended baseline from `references/reference-profile.md` and the bundled assets directly.
5. Build the execution sequence with `scripts/plan_bootstrap.sh`.
   - Use `inspect` mode when the user wants a plan only.
   - Use `apply-user` when sudo is unavailable or intentionally avoided.
   - Use `apply-sudo` only when system package installation and `chsh` are expected.
6. Execute with `scripts/apply_bootstrap.sh` when the user wants changes applied.
   - Start with `--dry-run` unless the user explicitly wants immediate mutation.
   - Use `--mode user` for user-space bootstrap only.
   - Use `--mode sudo` only when package installation and optional shell switch are allowed.
7. Use `scripts/install_system_packages.sh` when a root session is available and only a minimal system package set should be installed.
   - Keep `fzf` and `pixi` in user space by default.
   - Restrict system packages to shell and multiplexer prerequisites unless the user explicitly asks for more.

## Operating Rules

- Prefer user-space installation paths when sudo is unavailable.
- Never migrate API keys, tokens, proxy exports, or machine-specific absolute paths by default.
- Back up existing remote dotfiles before replacing them.
- Keep the shared config minimal and additive. Favor `.local` includes for host-specific customization.
- When package availability is uncertain, report the gap and continue with the remaining safe steps.

## Script Entry Points

- `scripts/inspect_host.sh [user@]host`
  - Emit a tagged report for local or remote machine facts.
- `scripts/classify_local_dotfiles.sh [file ...]`
  - Classify dotfile lines into safe, parameterized, and blocked buckets.
- `scripts/render_safe_zshrc.sh`
  - Print a reusable zshrc template to stdout.
- `scripts/plan_bootstrap.sh [user@]host`
  - Combine host facts with migration policy and print the recommended sequence.
- `scripts/apply_bootstrap.sh [--mode user|sudo] [--dry-run] [user@]host`
  - Copy shared assets, render a safe zshrc, install pixi in user space, and optionally install base packages.
- `scripts/install_system_packages.sh [root@]host`
  - Install the minimal system package baseline and switch the target user to zsh when appropriate.

## References

- Read `references/compatibility.md` for Rocky/RHEL-oriented package and privilege behavior.
- Read `references/migration-policy.md` when deciding whether a local config fragment is safe to reuse.
- Read `references/reference-profile.md` when the user wants a recommended setup without copying the current machine's dotfiles.

## Bundled Assets

- `assets/amuse-yx.zsh-theme`
  - Copy to `${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/`.
- `assets/tmux.conf`
  - Use as the shared tmux baseline.
- `assets/bash_aliases.sh`
  - Copy to `$HOME/.config/dev-bootstrap/bash_aliases.sh` or another stable path and source it from local shell config.
- `assets/tmux.conf`, `assets/bash_aliases.sh`, `assets/amuse-yx.zsh-theme`, and `scripts/render_safe_zshrc.sh`
  - Together form the recommended baseline profile when no local migration is desired.

## Output Expectations

- In `inspect`, produce a concise inventory plus concrete risks and next steps.
- In `plan`, produce a decision-complete bootstrap sequence with explicit sudo assumptions.
- In `apply`, describe what will change before running commands, then verify the result with a follow-up inspection.
