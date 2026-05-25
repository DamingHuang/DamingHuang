# 🛠️ Troubleshooting — homelab-media

---

## 1. YAML Syntax Error

**Error:**
```
environment:S
```

**Cause:** Typo in `docker-compose.yml` — extra character after `environment:`.

**Fix:** Make sure there are no extra characters:
```yaml
environment:   # ✅ correct
environment:S  # ❌ wrong
```

---

## 2. mkdir fails on multiple folders (Windows)

**Error:**
```
A positional parameter cannot be found that accepts argument
```

**Cause:** PowerShell `mkdir` does not support creating multiple folders in one command.

**Fix:** Create folders one by one:
```powershell
mkdir C:\homelab-media
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

---

## 3. qBittorrent — Default Password Not Working

**Error:**
```
Unauthorized
```

**Cause:** LinuxServer's qBittorrent image generates a random temporary password on first startup. The default `admin / adminadmin` does not work.

**Fix:** Check the logs for the temporary password:
```bash
docker logs qbittorrent 2>&1 | findstr "password"
```

Output example:
```
The WebUI administrator password was not set. A temporary password is provided for this session: PugvLfCBI
```

Use the **last password** shown in the logs — it's the most recent one.

> ⚠️ After logging in, immediately change to your own password:
> **Tools → Options → Web UI → Password**

---

## 4. qBittorrent — IP Banned

**Error:**
```
Your IP address has been banned after too many failed authentication attempts.
```

**Cause:** Too many failed login attempts triggered an automatic ban.

**Fix:** Restart the container to clear the ban:
```bash
docker restart qbittorrent
```

Then immediately check logs for the new password and log in right away — don't wait too long.

---

## 5. qBittorrent — Password Still Not Working After Restart

**Cause:** Old config files retained the ban history even after restart.

**Fix:** Delete and recreate the config folder:
```bash
docker stop qbittorrent
```

```powershell
Remove-Item -Recurse -Force C:\homelab-media\config\qbittorrent\
mkdir C:\homelab-media\config\qbittorrent
```

```bash
docker start qbittorrent
docker logs qbittorrent 2>&1 | findstr "password"
```

Use the new password immediately after getting it.

---

## 6. Radarr — Cannot Connect to qBittorrent

**Error:**
```
Authentication Failure
```

**Cause:** After resetting qBittorrent config, the password stored in Radarr was outdated.

**Fix:**
1. Open http://localhost:7878
2. **Settings → Download Clients → qBittorrent**
3. Update the password to match your current qBittorrent password
4. Click **Test → Save**

---

## 7. Prowlarr — Cannot Connect to Radarr/Sonarr

**Error:**
```
Connection refused
```

**Cause:** Using `localhost` inside a Docker container refers to the container itself, not your Windows host machine.

**Fix:** Use your Windows machine's real IP address instead:
```powershell
# Find your IP
ipconfig | findstr "IPv4"
```

Then use it like:
```
http://192.168.1.38:7878   # Radarr
http://192.168.1.38:8989   # Sonarr
```

---

## 8. Prowlarr — Forgot Login Password

**Cause:** Authentication was manually enabled in Prowlarr settings.

**Fix:** Edit the config file directly:
```bash
docker stop prowlarr
```

```powershell
notepad C:\homelab-media\config\prowlarr\config.xml
```

Change these lines:
```xml
<!-- Before -->
<AuthenticationMethod>Forms</AuthenticationMethod>
<AuthenticationRequired>Enabled</AuthenticationRequired>

<!-- After -->
<AuthenticationMethod>None</AuthenticationMethod>
<AuthenticationRequired>DisabledForLocalAddresses</AuthenticationRequired>
```

```bash
docker start prowlarr
```

---

## 9. Indexer — 1337x Blocked by Cloudflare

**Error:**
```
Unable to access 1337x.to, blocked by CloudFlare Protection.
```

**Cause:** 1337x uses Cloudflare protection which blocks automated requests from Docker containers.

**Fix:** Use YTS instead — it's stable and has no Cloudflare protection:

1. Open Prowlarr http://localhost:9696
2. **Indexers → Add Indexer**
3. Search `YTS` → Add → Test → Save

> 💡 YTS specializes in high-quality movies (1080p/4K) with small file sizes — perfect for Radarr.

---

## 10. Torznab Indexer Returns 403

**Error:**
```
HTTP request failed: [403:Forbidden]
```

**Cause:** Public Torznab URLs (like `apibay.org`) are unstable and often block container requests.

**Fix:** Use Prowlarr + YTS instead of direct Torznab URLs. See issue #9 above.

---

## 11. Radarr — No Movie Files to Manage

**Symptom:**
```
Path: /data/downloads/Inception (2010)
No movie files to manage
```

**Cause:** Files were downloaded but not imported into Radarr's library.

**Fix:** Use Manual Import:
1. Go to **Movies → Manual Import**
2. Select the download folder
3. Radarr will automatically move the file to `/data/movies`

---

## ✅ Quick Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized` in qBittorrent | Random temp password | Check `docker logs qbittorrent` |
| IP banned | Too many failed logins | `docker restart qbittorrent` |
| Password still fails | Old config retained ban | Delete config folder and restart |
| Radarr auth failure | Outdated password after reset | Update password in Download Clients |
| Prowlarr connection refused | Used `localhost` instead of real IP | Use `ipconfig` to get real IP |
| 1337x Cloudflare blocked | Cloudflare protection | Switch to YTS indexer |
| 403 Torznab error | Unstable public URLs | Use Prowlarr + YTS |
| No movie files to manage | Files not imported | Use Manual Import in Radarr |
