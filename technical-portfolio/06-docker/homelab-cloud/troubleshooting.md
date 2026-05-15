# 🛠️ Troubleshooting

## Vaultwarden — Insecure URL not allowed

**Error:**
```
Insecure URL not allowed. All URLs must use HTTPS.
```

**Cause:** Vaultwarden requires HTTPS. HTTP is not allowed.

**Fix — Add Caddy for local HTTPS:**

1. Add to `volumes:` section:
```yaml
  caddy_data:
  caddy_config:
```

2. Add to `services:` section:
```yaml
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    networks:
      - internal
    ports:
      - "8443:8443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
```

3. Update vaultwarden `environment:`:
```yaml
    environment:
      SIGNUPS_ALLOWED: "true"
      DOMAIN: "https://localhost:8443"
```

4. Create `Caddyfile` (no extension) in project root:
```powershell
New-Item -Path "C:\homelab-cloud\Caddyfile" -ItemType File
notepad C:\homelab-cloud\Caddyfile
```

Paste the following content:
```
{
    local_certs
}

localhost:8443 {
    reverse_proxy vaultwarden:80
}
```

5. Restart services:
```bash
docker compose up -d
```

Access Vaultwarden at 👉 **https://localhost:8443**

> ⚠️ Browser will warn about the certificate — click "Advanced" → "Proceed" to continue.

---

## Port already allocated

**Error:**
```
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Fix:** Change the port number in `docker-compose.yml`:
```yaml
ports:
  - "8083:80"   # change the left number to any available port
```

Then restart:
```bash
docker compose up -d
```

---

## mkdir fails on multiple folders (Windows)

**Error:**
```
A positional parameter cannot be found that accepts argument
```

**Fix:** Create folders one by one in PowerShell:
```powershell
mkdir docs
mkdir configs
mkdir configs\traefik
mkdir configs\nextcloud
```

---

## Immich slow to start

**Cause:** First startup downloads AI models (~1-2 GB).

**Fix:** Wait 3-5 minutes, then check logs:
```bash
docker compose logs -f immich_server
```

Ready when you see:
```
Immich Server is listening on port 2283
```

