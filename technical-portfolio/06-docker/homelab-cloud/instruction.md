# 🏠 homelab-cloud — Local Setup Guide

## Prerequisites

```bash
docker --version        # Verify Docker is installed
docker compose version  # Verify Docker Compose is installed
```

---

## Step 1 — Create Project Folder

```powershell
cd C:\
mkdir homelab-cloud
cd C:\homelab-cloud
mkdir configs
mkdir configs\traefik
mkdir configs\nextcloud
```

---

## Step 2 — Install Nextcloud

Create `docker-compose.yml` in `C:\homelab-cloud\` with the following content:

```yaml
version: "3.8"

networks:
  internal:

volumes:
  nextcloud_data:
  nextcloud_db:

services:

  nextcloud_db:
    image: mariadb:11
    container_name: nextcloud_db
    restart: unless-stopped
    networks:
      - internal
    volumes:
      - nextcloud_db:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword123
      MYSQL_DATABASE: nextcloud
      MYSQL_USER: nextcloud
      MYSQL_PASSWORD: ncpassword123

  nextcloud:
    image: nextcloud:28-apache
    container_name: nextcloud
    restart: unless-stopped
    depends_on:
      - nextcloud_db
    networks:
      - internal
    ports:
      - "8083:80"
    volumes:
      - nextcloud_data:/var/www/html
    environment:
      MYSQL_HOST: nextcloud_db
      MYSQL_DATABASE: nextcloud
      MYSQL_USER: nextcloud
      MYSQL_PASSWORD: ncpassword123
      NEXTCLOUD_ADMIN_USER: admin
      NEXTCLOUD_ADMIN_PASSWORD: admin123
```

Start the service:

```bash
docker compose up -d
```

Access Nextcloud at 👉 **http://localhost:8083**

---

## Step 3 — Install Immich

Add the following to the `volumes:` section:

```yaml
  immich_data:
  immich_db:
```

Add the following to the `services:` section:

```yaml
  immich_db:
    image: tensorchord/pgvecto-rs:pg16-v0.2.0
    container_name: immich_db
    restart: unless-stopped
    networks:
      - internal
    volumes:
      - immich_db:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: immich
      POSTGRES_USER: immich
      POSTGRES_PASSWORD: immichpassword123

  immich_redis:
    image: redis:7-alpine
    container_name: immich_redis
    restart: unless-stopped
    networks:
      - internal

  immich_machine_learning:
    image: ghcr.io/immich-app/immich-machine-learning:release
    container_name: immich_ml
    restart: unless-stopped
    networks:
      - internal
    volumes:
      - immich_data:/usr/src/app/upload

  immich_server:
    image: ghcr.io/immich-app/immich-server:release
    container_name: immich_server
    restart: unless-stopped
    depends_on:
      - immich_db
      - immich_redis
    networks:
      - internal
    ports:
      - "2283:2283"
    volumes:
      - immich_data:/usr/src/app/upload
    environment:
      DB_HOSTNAME: immich_db
      DB_DATABASE_NAME: immich
      DB_USERNAME: immich
      DB_PASSWORD: immichpassword123
      REDIS_HOSTNAME: immich_redis
```

```bash
docker compose up -d
```

Access Immich at 👉 **http://localhost:2283**

> ⚠️ First startup may take 3-5 minutes — Immich downloads AI models in the background.

---

## Step 4 — Install Vaultwarden

Add the following to the `volumes:` section:

```yaml
  vaultwarden_data:
```

Add the following to the `services:` section:

```yaml
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    restart: unless-stopped
    networks:
      - internal
    ports:
      - "8090:80"
    volumes:
      - vaultwarden_data:/data
    environment:
      SIGNUPS_ALLOWED: "true"
```

```bash
docker compose up -d
```

Access Vaultwarden at 👉 **http://localhost:8090**

---

## ✅ All Services Running

| Service | URL |
|---------|-----|
| Nextcloud | http://localhost:8083 |
| Immich | http://localhost:2283 |
| Vaultwarden | http://localhost:8090 |



