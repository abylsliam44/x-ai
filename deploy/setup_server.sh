#!/usr/bin/env bash
# setup_server.sh — one-time Ubuntu 22.04 server bootstrap
# Run as root (or with sudo) on a fresh DigitalOcean droplet.
set -euo pipefail

echo "==> Updating packages..."
apt-get update -y && apt-get upgrade -y

echo "==> Installing prerequisites..."
apt-get install -y \
  curl git ufw ca-certificates gnupg lsb-release \
  software-properties-common apt-transport-https

# --- Docker ---
echo "==> Installing Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

echo "==> Adding current user to docker group (re-login required)..."
usermod -aG docker "${SUDO_USER:-$(whoami)}"

# --- Swap (4 GB) ---
if [ ! -f /swapfile ]; then
  echo "==> Creating 4 GB swap..."
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  sysctl vm.swappiness=10
  echo 'vm.swappiness=10' >> /etc/sysctl.conf
fi

# --- UFW firewall ---
echo "==> Configuring UFW..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   comment "SSH"
ufw allow 80/tcp   comment "HTTP"
ufw allow 443/tcp  comment "HTTPS"
ufw --force enable

echo ""
echo "==> Server setup complete."
echo "    IMPORTANT: log out and back in so the docker group takes effect."
