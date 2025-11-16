# Spotify Library Manager
Originally derived as a fork of [glomatico/spotify-aac-downloader](https://github.com/glomatico/spotify-aac-downloader), this has grown into a completely different behemoth.

This started as a simple want to mass-download songs for specific artists since they were not otherwise available, and snowballed into a full-fledged library management platform including:
- Task queuing system, allowing downloads to continue after restarts*
  - *Semi-lossy, where jobs which are interrupted will not be recovered, but any un-started jobs will be. Jobs can safely be restarted manually, though.
- Artist discography syncing and mass-downloading
- Artist tracking - auto downloading missing releases (including new)
- Fetch metadata for all albums available for tracked artists
- Mark un-downloaded albums as non-wanted
  - Useful for artists which have a large backlog of music you don't want, but you still want to track their latest stuff automatically
- Download all "wanted" albums (via queued tasks)
- Download playlists/albums directly
  - Can choose to auto mark all artists on given playlists as "Tracked", useful for "favourites" playlists
- Tracked playlist syncing
 - Can continuously refresh and sync (every 4 hours)
 - Can include auto-tracking new artists (such as tracking a "favourites" playlist)
- Artist tracking supporting auto-downloading newly released albums (including tracks)
 - Can continuously refresh and sync (every 6 hours)
 - Will download missing releases (every 6 hours, offset by 45 minutes)

Features from spotify-aac-downloader:
* Download songs in 128kbps AAC or 256kbps AAC with a premium account
* Download synced lyrics
* Includes a device wvd so no need to load your own!
     
## Notes
While this has a lot of opportunity to improve, it's reached a "stable" state for my personal usage. Therefore I will fix critical issues as I encounter them, but will not actively be working on additional features except when inspiration hits me, or there are specific community requests.

If there is enough desire from folks, I am happy to put more time in, and of course always welcome Pull Requests!

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup instructions and guidelines.

## Security & Authentication

**⚠️ Important Security Notice**: This application **does not include built-in authentication**. It is designed for personal use in trusted environments.

### If You Need Authentication

If you plan to expose this application externally or want to add authentication, consider:

- **Reverse proxy with authentication**: Use [Traefik](https://traefik.io/) with auth middleware, [nginx](https://nginx.org/) with auth modules, or [Caddy](https://caddyserver.com/) with auth plugins
- **Authentication gateways**:
  - [Authentik](https://goauthentik.io/) - Self-hosted identity provider
  - [Authelia](https://www.authelia.com/) - Lightweight authentication and authorization server
  - [OAuth2 Proxy](https://oauth2-proxy.github.io/oauth2-proxy/) - OAuth2 and OIDC authentication proxy
- **VPN access**: Keep the application internal and access via VPN (WireGuard, OpenVPN, etc.)
- **Network-level protection**: Firewall rules, VPC isolation, or private networks only

### Security Best Practices

- **Never expose this application directly to the internet** without proper authentication
- **Use HTTPS** in production environments with proper TLS certificates
- **Keep the application updated** and monitor for security advisories
- **Limit network access** to trusted users and networks only
- **Regular backups** of your configuration and database

## Migration from Previous Versions

**⚠️ Breaking Changes**: This version includes major infrastructure changes (Huey→Celery, SQLite→PostgreSQL, Docker-first development). 

### Quick Migration (Docker Users)
```bash
docker compose down -v && git pull && docker compose up -d
```

### Full Migration Guide
For development setups or data preservation, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed instructions.

## TODO
### Features To Add:
- [ ] Fallback to yt-dlp when no Spotify AAC
- [X] Tracked Playlists
  - [ ] Improve update experience (not URL-locked)
- [ ] Allow periodic tasks to be configurable intervals
- [ ] Add artists directly (by artist name?)

### Other Changes:
- [ ] Re-add Downloader configuration(s) loading via `settings.yaml`
- [ ] Improve onboarding documentation
  - [ ] Add critical steps such as first startup, any missing examples, etc

## Screenshots
![Main Dashboard](https://github.com/Kyrluckechuck/spotify-library-manager/assets/7606153/6d32f8d5-fe6b-4884-a5a9-7970aaba284a)
![Example Artist Page](https://github.com/Kyrluckechuck/spotify-library-manager/assets/7606153/2dcceee2-41e4-4101-b257-2ca754017c20)



## Configuration / Usage
It's currently being designed to mostly run on Linux-based systems, however, many of the configurations should only require minor tweaks to adjust for Windows-based systems.

Existing settings (that are applicable) are now set via `/config/settings.yaml`, and will override any default configurations.

Quick start:

1. Copy the example file and adjust values
   ```bash
   cp api/settings.yaml.example /config/settings.yaml
   ```
2. Edit `/config/settings.yaml` (mounted volume) to fit your environment:
   ```yaml
   default:
     # Where downloaded music is stored
     final_path: "/mnt/music_spotify"

     # Downloader defaults
     cookies_location: "/config/cookies.txt"
     log_level: INFO
     no_lrc: false
     overwrite: false

     # Album selection
     ALBUM_TYPES_TO_DOWNLOAD: [single, album, compilation]
     ALBUM_GROUPS_TO_IGNORE: [appears_on]
   ```

Notes:
- You can also set environment variables to override YAML at runtime.
- Secrets like `DJANGO_SECRET_KEY` should be set via env vars.

## Running From Docker (recommended)
An example compose setup is included. Follow these steps:

1. Prepare a local config directory and files:
   ```bash
   mkdir -p ./config/db
   # Export cookies from your browser while logged into Spotify
   # Save as ./config/cookies.txt
   # Optional: place your Widevine device file as ./config/device.wvd
   # Create ./config/settings.yaml with your desired overrides (see earlier example)
   ```

2. Create an environment file from the example and set paths:
   ```bash
   cp .env.example .env
   # Edit .env and set SLM_CONFIG_DIR to the absolute path of ./config, e.g.:
   # SLM_CONFIG_DIR="${PWD}/config"
   # Optionally set MUSIC_DIR to where downloads should be stored
   ```

3. Bring up the stack:
   ```bash
   docker compose up --build -d
   ```

4. Access the app:
   - **Development**: http://localhost:3000 (Frontend dev server with HMR)
   - **Production**: http://localhost:5000 (Nginx serving frontend + API)

5. Useful commands:
   ```bash
   docker compose logs -f                # tail all services
   docker compose logs -f web            # API logs
   docker compose logs -f frontend       # Frontend logs
   docker compose logs -f worker         # Worker logs
   docker compose down -v                # stop and remove volumes
   ```

## Running From Source (Development)

> [!NOTE]
> This setup is optimized for development with proper async processing and background task handling.

### Prerequisites
1. Install Python 3.13 or higher
2. Install Node.js and Yarn
3. Place your cookies in `/config/` as `cookies.txt`
   * You can export your cookies by using this Google Chrome extension on Spotify website: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc. Make sure to be logged in.

### Quick Start
1. **Setup dependencies:**
   ```bash
   make setup
   ```

2. **Start the development environment:**
   ```bash
   make dev
   ```
   
   This starts all three services:
   - **API Server** (http://localhost:5000/graphql)
   - **Frontend Server** (http://localhost:3000)
   - **Celery Worker** (background task processing)

3. **Test the setup:**
   ```bash
   python test_dev_setup.py
   ```

### Development Commands (All Run From Root)

All commands can be run from the root directory without any `cd` commands. All configuration and dependency files have been moved to the root for a cleaner structure:

**Main Development:**
- `make dev` - Start all services (API, Frontend, Worker)
- `make dev-api` - Start only the API server
- `make dev-frontend` - Start only the frontend dev server
- `make dev-worker` - Start only the Celery worker

**Installation:**
- `make install` - Install both API and frontend dependencies
- `make install-api` - Install only API dependencies
- `make install-frontend` - Install only frontend dependencies

**Testing & Quality:**
- `make test` - Run tests for both API and frontend
- `make lint` - Run linting for both API and frontend
- `make build` - Build the frontend

**Database:**
- `make migrate` - Run Django migrations
- `make createsuperuser` - Create Django superuser

**Docker:**
- `make docker-build` - Build Docker image
- `make docker-run` - Run with docker-compose
- `make docker-stop` - Stop docker-compose

**Utilities:**
- `make clean` - Clean build artifacts
- `make setup` - Original setup command

### Development Features

#### ✅ **Optimized Async Processing**
- Background tasks are properly queued and processed
- Non-blocking UI operations
- Real-time task progress updates
- Multiple worker threads for parallel processing

#### ✅ **Enhanced Monitoring**
- Color-coded service logs: `[WEB]`, `[FRONTEND-DEV]`, `[WORKER]`, `[BEAT]`, `[POSTGRES]`
- Service health checks and validation
- Background task indicators in the UI
- Graceful error handling and recovery

#### ✅ **Performance Optimizations**
- Celery workers for parallel task processing
- PostgreSQL-backed task queue for reliability
- Faster task execution and reduced latency
- Higher concurrency limits for the API server

### Configuration

For development, you can customize the Celery settings in `api/settings.py`:

```python
CELERY_BROKER_URL = 'db+postgresql://...'  # PostgreSQL as message broker
CELERY_RESULT_BACKEND = 'db+postgresql://...'  # Results stored in PostgreSQL
CELERY_WORKER_CONCURRENCY = 4  # Number of worker processes
CELERY_TASK_ALWAYS_EAGER = False  # Async task execution
```

**Periodic Task Management:**
- **Docker mode**: Access Django admin via shell: `docker compose exec web python manage.py shell`
- **Local mode**: Django admin at http://localhost:5000/admin/django_celery_beat/
- Alternatively, edit schedules directly in `api/celery_beat_schedule.py`

### Troubleshooting

If you encounter issues:

1. **Check service status:**
   ```bash
   docker compose ps
   ```

2. **Verify Celery worker is running:**
   - Check worker logs: `docker compose logs worker`
   - Check beat scheduler logs: `docker compose logs beat`

3. **Reset the environment:**
   ```bash
   make setup
   make dev
   ```

### Development Notes

- The system now properly handles async operations with real background task processing
- Tasks like artist sync, playlist downloads, and album fetching are processed asynchronously
- The UI remains responsive during background operations
- All services are monitored and will restart automatically if they fail

For more details on the optimizations, see [DEVELOPMENT_OPTIMIZATIONS.md](DEVELOPMENT_OPTIMIZATIONS.md).

## Upgrading from the legacy Django app

If you are upgrading from the older repository layout where the Django app lived at `spotify_library_sync/library_manager` with migrations `0001`–`0020`, this branch consolidates that history into a new `library_manager` app with a fresh `0001_initial` that declares `replaces` for the legacy chain. This prevents migration history conflicts.

Recommended steps:

1. Back up your database.
2. Inspect the current migration state:
   ```bash
   # From repo root
   cd api
   python manage.py showmigrations library_manager
   ```
3. Apply migrations normally:
   ```bash
   python manage.py migrate
   ```
4. Only if you see errors about tables already existing for `library_manager` (e.g., upgrading from a DB that has tables but missing migration records), re-run with:
   ```bash
   python manage.py migrate --fake-initial
   ```

Notes:
- The new `0001_initial` includes a `replaces = [...]` list mapping all legacy migrations, so environments that had applied those will upgrade cleanly.
- Fresh installations are unaffected and will run the new migration sequence as normal.

## Configuration (IGNORE, Half-updated and docker is the intended use)
> [!CAUTION]
> TO BE MIGRATED TO `settings.yaml` -- THESE WILL CHANGE NOTHING PRESENTLY

spotify-aac-downloader can be configured using the command line arguments or the config file. The config file is created automatically when you run spotify-aac-downloader for the first time at `~/.spotify-aac-downloader/config.json` on Linux and `%USERPROFILE%\.spotify-aac-downloader\config.json` on Windows. Config file values can be overridden using command line arguments.
| Command line argument / Config file key                         | Description                                                           | Default value                                       |
| --------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------- |
| `-c`, `--cookies-location` / `cookies_location`                 | Location of the cookies file.                                         | `./cookies.txt`                                     |
| `-w`, `--po-token` / `po_token`                                 | PO Token for your Youtube Music account                                            | `null`                                              |
| `--config-location` / -                                         | Location of the config file.                                          | `<home_folder>/.spotify-aac-downloader/config.json` |
| `-l`, `--log-level` / `log_level`                               | Log level.                                                            | `INFO`                                              |
| `-n`, `--no-lrc` / `no_lrc`                                     | Don't download the synced lyrics.                                     | `false`                                             |
| `-o`, `--overwrite` / `overwrite`                               | Overwrite existing files.                                             | `false`                                             |
| `--print-exceptions` / `print_exceptions`                       | Print exceptions.                                                     | `false`                                             |
| `-u`, `--url-txt` / -                                           | Read URLs as location of text files containing URLs.                  | `false`                                             |
| `-n`, `--no-config-file` / -                                    | Don't use the config file.                                            | `false`                                             |
