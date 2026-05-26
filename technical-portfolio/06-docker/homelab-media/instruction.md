# 🏠 homelab-media — Local Setup Guide

## Prerequisites

```bash
docker --version        # Verify Docker is installed
docker compose version  # Verify Docker Compose is installed
```

---

## Step 1 — Create Project Folder

```powershell
cd C:\
mkdir homelab-media
cd C:\homelab-media
mkdir configs
mkdir configs\jellyfin
mkdir configs\sonarr
mkdir configs\radarr
mkdir configs\qbittorrent
mkdir configs\prowlarr
mkdir data
mkdir data\movies
mkdir data\tv
mkdir data\downloads
```

> ⚠️ On Windows PowerShell, create folders one by one — multiple folders in one command will cause an error.

---

## Step 2 — Create docker-compose.yml

Create `docker-compose.yml` in `C:\homelab-media\` with the following content:

```yaml
version: '3.8'
services:

  jellyfin:
    image: lscr.io/linuxserver/jellyfin:latest
    container_name: jellyfin
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - ./config/jellyfin:/config
      - ./data:/data
      - ./data/downloads:/downloads
    ports:
      - 8096:8096
    restart: unless-stopped

  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - ./config/sonarr:/config
      - ./data:/data
    ports:
      - 8989:8989
    restart: unless-stopped

  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - ./config/radarr:/config
      - ./data:/data
    ports:
      - 7878:7878
    restart: unless-stopped

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - ./config/qbittorrent:/config
      - ./data/downloads:/downloads
    ports:
      - 8080:8080
      - 6881:6881
      - 6881:6881/udp
    restart: unless-stopped

  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Shanghai
    volumes:
      - ./config/prowlarr:/config
    ports:
      - 9696:9696
    restart: unless-stopped
```

Start all services:

```bash
docker compose up -d
```

---

## Step 3 — Configure qBittorrent

1. Get your temporary password:
```bash
docker logs qbittorrent 2>&1 | findstr "password"
```

Output example:
```
The WebUI administrator password was not set. A temporary password is provided for this session: PugvLfCBI
```

> ⚠️ Use the **last password** shown in the logs.

2. Open http://localhost:8080
3. Login with:
   - Username: `admin`
   - Password: the temporary password from logs

4. **Immediately change to your own password:**
   **Tools → Options → Web UI → Password → Save**

---

## Step 4 — Get Your Windows IP Address

Radarr and Sonarr need your real IP to connect to other containers.

```powershell
ipconfig | findstr "IPv4"
```

Note down the IP address, e.g. `192.168.1.38`

> ⚠️ Do NOT use `localhost` — it won't work inside Docker containers.

---

## Step 5 — Connect Radarr to qBittorrent

1. Open http://localhost:7878
2. **Settings → Download Clients → ➕**
3. Select **qBittorrent**
4. Fill in:

```
Host:     192.168.1.xx   (your real IP from Step 4)
Port:     8080
Username: admin
Password: your qBittorrent password
Category: radarr
```

5. Click **Test** → should show ✅
6. Click **Save**

---

## Step 6 — Connect Sonarr to qBittorrent

1. Open http://localhost:8989
2. **Settings → Download Clients → ➕**
3. Select **qBittorrent**
4. Fill in the same details as Step 5, but change Category to `sonarr`
5. Click **Test → Save**

---

## Step 7 — Add YTS Indexer in Prowlarr

1. Open http://localhost:9696
2. Click **Indexers → ➕ Add Indexer**
3. Search `YTS` → click **➕**
4. Click **Test → Save**

> 💡 YTS specializes in high-quality movies (1080p/4K) with small file sizes.
> Do NOT use 1337x — it is blocked by Cloudflare in Docker environments.

---

## Step 8 — Connect Prowlarr to Radarr

1. In Prowlarr, go to **Settings → Apps → ➕**
2. Select **Radarr**
3. Fill in:

```
Prowlarr Server: http://localhost:9696
Radarr Server:   http://192.168.1.xx:7878   (your real IP)
API Key:         (copy from Radarr → Settings → General → API Key)
```

4. Click **Test → Save**
5. YTS will automatically sync to Radarr

---

## Step 9 — Connect Prowlarr to Sonarr

1. In Prowlarr, go to **Settings → Apps → ➕**
2. Select **Sonarr**
3. Fill in:

```
Prowlarr Server: http://localhost:9696
Sonarr Server:   http://192.168.1.xx:8989   (your real IP)
API Key:         (copy from Sonarr → Settings → General → API Key)
```

4. Click **Test → Save**

---

## Step 10 — Test: Search and Download a Movie

1. Open http://localhost:7878
2. **Movies → Add New Movie**
3. Search `Inception`
4. Select quality **HD-1080p**
5. Click **Add Movie**
6. Go to **Wanted → Missing**
7. Click **Search All**
8. Check http://localhost:8080 — download should appear in qBittorrent

---

## ✅ All Services Running

| Service | URL | Purpose |
|---------|-----|---------|
| Jellyfin | http://localhost:8096 | Media player |
| Radarr | http://localhost:7878 | Movie management |
| Sonarr | http://localhost:8989 | TV show management |
| qBittorrent | http://localhost:8080 | Downloader |
| Prowlarr | http://localhost:9696 | Indexer management |

---

## How It All Works Together

```
Prowlarr (YTS Indexer)
        ↓ auto sync
Radarr (Movies) ──┐
Sonarr (TV)     ──┼──► qBittorrent (Download) ──► Jellyfin (Play)
```

---

> ⚠️ For common errors and fixes, see [troubleshooting.md](troubleshooting.md)
