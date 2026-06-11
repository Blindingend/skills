# Compatibility Notes

## Linux baseline

- Treat Linux as the primary target for this skill.
- Expect fresh hosts to have only `bash`, `git`, `curl` or `wget`, and a package manager.
- Prefer probing the package manager instead of guessing distro family from memory.

## Rocky / RHEL family

- Expect `dnf` on Rocky Linux 8/9 and related RHEL-family systems.
- Some hosts may have incomplete Rocky repo definitions. If `baseos` is missing, add it before trying to install `zsh` or `tmux`.
- In restricted environments, `sudo -n true` often fails even when sudo exists. Distinguish:
  - `sudo` missing
  - `sudo` installed but password required
  - passwordless sudo available
- Common first-wave system packages are usually `zsh`, `tmux`, and optionally `ripgrep`.
- Keep `fzf`, `pixi`, `zsh-autosuggestions`, and `zsh-syntax-highlighting` in user space by default.
- User-space `pixi` installation is a good fallback when system package installation is blocked.
- If third-party repos fail GPG verification, disable only the failing repos for the transaction instead of weakening global GPG checks.
- Do not assume `neovim`, `fd`, `bat`, or `eza` exist in default repos.

## Shell migration

- Shared shell config should only include portable exports and plugin initialization.
- Keep `PATH` additions generic when possible:
  - good: `$HOME/.local/bin`, `$HOME/.pixi/bin`
  - bad: `/opt/company/toolchain/bin`, `/home/user/node-vXX/bin`
- Add `~/.zshrc.local` as the host override point.

## Remote execution

- Use `ssh -o BatchMode=yes -o ConnectTimeout=5` for quick non-interactive detection.
- For reporting, prefer tagged sections over free-form prose so later commands can parse results.
- If an inspection command fails, return partial facts rather than aborting the whole workflow.
