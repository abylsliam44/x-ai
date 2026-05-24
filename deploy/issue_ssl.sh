#!/usr/bin/env bash
# issue_ssl.sh — obtain/renew Let's Encrypt certs through Docker certbot.
# Usage: ./deploy/issue_ssl.sh [domain] [email]
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

DOMAIN="${1:-${DOMAIN:-}}"
EMAIL="${2:-${LETSENCRYPT_EMAIL:-}}"

if [ -z "$DOMAIN" ] || [[ "$DOMAIN" == *"YOUR_DOMAIN"* ]]; then
  echo "Usage: $0 <domain> <email>"
  echo "ERROR: domain is missing. You can also set DOMAIN in root .env."
  exit 1
fi

if [ -z "$EMAIL" ] || [[ "$EMAIL" == *"YOUR_DOMAIN"* ]]; then
  echo "Usage: $0 <domain> <email>"
  echo "ERROR: email is missing. You can also set LETSENCRYPT_EMAIL in root .env."
  exit 1
fi

domains=(-d "$DOMAIN")
if [[ "$DOMAIN" != www.* ]]; then
  domains+=(-d "www.$DOMAIN")
fi

echo "==> Ensuring nginx is running for ACME webroot challenge..."
docker compose -f docker-compose.prod.yml up -d nginx

echo "==> Requesting certificate for: ${domains[*]}"
docker compose -f docker-compose.prod.yml --profile ssl run --rm certbot \
  certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  "${domains[@]}"

echo "==> Enabling HTTPS nginx config..."
sed "s/__DOMAIN__/${DOMAIN//\//\\/}/g" \
  nginx/conf.d/app.https.template > nginx/conf.d/app.conf

echo "==> Validating and reloading nginx..."
docker compose -f docker-compose.prod.yml exec nginx nginx -t
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "==> HTTPS is configured for https://$DOMAIN"
