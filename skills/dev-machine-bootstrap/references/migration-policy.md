# Migration Policy

## Safe by default

- `tmux` key bindings and status bar config
- Generic `zsh` plugin lists
- Reusable aliases and shell helper functions that do not hardcode local infrastructure
- Theme files
- Safe git identity fields such as `user.name` and `user.email`

## Parameterize before migration

- Editor selection
- `PATH` or `LD_LIBRARY_PATH` changes
- Language-specific environment setup such as `nvm`, Java, Go, or Conda initialization
- Global git ignore paths
- SSH completion sources or host lists

## Block by default

- API keys, access tokens, cookies, and credentials
- Proxy variables and company-network routing exports
- Machine-specific absolute paths
- Host-only service endpoints
- Anything that references secrets in clear text

## Decision rule

- If a line contains a secret or network routing intent, block it.
- If a line references a specific machine path or toolchain location, classify it as parameterized.
- If a line configures editor behavior, prompt theme, plugins, aliases, or tmux behavior without host assumptions, classify it as safe.
