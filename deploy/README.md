# Deployment Guide

Target: Ubuntu 22.04 on DigitalOcean (2 vCPU / 2 GB RAM minimum, 4 GB recommended).

## First-time server setup

```bash
# On the server as root:
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/deploy/setup_server.sh | bash
```

This installs Docker, Docker Compose plugin, configures a 4 GB swapfile, and opens ports 22/80/443 via UFW.

## Environment configuration

```bash
# On the server, inside the project root:
cp .env.production.example .env
nano .env            # Fill POSTGRES_PASSWORD, DOMAIN, LETSENCRYPT_EMAIL

cp backend/.env.production.example backend/.env
nano backend/.env   # Fill in: SECRET_KEY, OPENAI_API_KEY, X_CLIENT_ID, X_CLIENT_SECRET
```

**Required secrets:**
| Variable | Description |
|---|---|
| `SECRET_KEY` | 64-char random hex — `python -c "import secrets; print(secrets.token_hex(32))"` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `X_CLIENT_ID` | X Developer app Client ID |
| `X_CLIENT_SECRET` | X Developer app Client Secret |
| `X_REDIRECT_URI` | Must match your registered redirect URI exactly |
| `POSTGRES_PASSWORD` | Root `.env`; at least 16 chars, not `postgres` |

## Deploy

```bash
# From the project root:
./deploy/deploy.sh
```

This:
1. Validates that secrets are filled in
2. Builds the frontend (`npm run build` via Docker)
3. Builds/pulls Docker images
4. Starts all services
5. Runs database migrations
6. Verifies the health endpoint

## Health check

```bash
./deploy/check_health.sh
```

## Database backup / restore

```bash
# Backup
./deploy/backup_db.sh

# Restore a specific backup
./deploy/restore_db.sh backups/agentic_x_20240101_120000.sql.gz
```

## SSL / HTTPS with Let's Encrypt

Obtain a certificate through the Docker certbot service:

```bash
./deploy/issue_ssl.sh yourdomain.com admin@yourdomain.com
```

This uses the shared certbot Docker volumes, writes the HTTPS nginx config from
`nginx/conf.d/app.https.template`, validates nginx, and reloads it.

## Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Single service
docker compose -f docker-compose.prod.yml logs -f backend
```

## Updating the application

```bash
git pull origin main
./deploy/deploy.sh
```

## X Developer Portal configuration

After deploying, set the **Callback URI** in your X Developer Portal app settings to:

```
https://your-domain.com/api/v1/x/callback
```

Set `X_REDIRECT_URI` in `backend/.env` to the same value.
