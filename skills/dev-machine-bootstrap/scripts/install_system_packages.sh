#!/usr/bin/env bash
set -euo pipefail

target="${1:?Usage: $0 [root@]host}"
target_user="${TARGET_USER:-yanxin}"

ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "
set -e
if ! dnf repolist --all 2>/dev/null | grep -q '^baseos[[:space:]]'; then
  cat >/etc/yum.repos.d/rocky-baseos.repo <<'EOF'
[baseos]
name=Rocky Linux \$releasever - BaseOS
mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=\$basearch&repo=BaseOS-\$releasever\$rltype
#baseurl=http://dl.rockylinux.org/\$contentdir/\$releasever/BaseOS/\$basearch/os/
gpgcheck=1
enabled=1
countme=1
metadata_expire=6h
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
EOF
  dnf clean all >/dev/null 2>&1 || true
fi
if command -v dnf >/dev/null 2>&1; then
  dnf --disablerepo=runner_gitlab-runner --disablerepo=runner_gitlab-runner-source install -y zsh tmux ripgrep
elif command -v apt >/dev/null 2>&1; then
  apt update
  apt install -y zsh tmux ripgrep
else
  echo 'Unsupported package manager for install_system_packages.sh' >&2
  exit 1
fi
if command -v chsh >/dev/null 2>&1 && command -v zsh >/dev/null 2>&1; then
  chsh -s \"\$(command -v zsh)\" \"$target_user\" || true
fi
"
