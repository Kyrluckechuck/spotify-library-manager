# Migration Guide: Huey to Celery + Infrastructure Overhaul

This guide covers migrating from the previous Huey-based system to the new Celery + PostgreSQL infrastructure.

## 🐳 **Docker Users (Simple Migration)**

If you're using Docker with the `master` branch, migration is mostly automated:

```bash
# Stop existing containers
docker compose down -v

# Pull latest changes
git pull origin master

# Start with new infrastructure (auto-migrates)
docker compose up -d

# Database migrations run automatically on startup
# Your existing music files are preserved
```

**That's it!** The new system will:
- ✅ Automatically run database migrations
- ✅ Preserve your existing music downloads  
- ✅ Set up Celery task queue with PostgreSQL
- ✅ Start the new TanStack Router frontend

> **Note**: Task history from Huey will be lost (incompatible systems), but your artists, albums, and music files remain untouched.

---

## 🛠️ **Manual/Development Migration (Advanced)**

The following sections are for **development setups** or users who need **data preservation** from non-Docker installations.

## 🚨 **Breaking Changes Overview**

### Major System Changes
- **Task Queue**: Huey → Celery with PostgreSQL broker
- **Database**: SQLite → PostgreSQL (unified for app data + task queue)
- **Development**: Mixed setup → Docker-first workflow
- **Routing**: Legacy → TanStack Router (frontend)
- **Configuration**: Scattered → Centralized in `/config/`

## 🔄 **Migration Steps**

### 1. **Backup Your Data**
```bash
# Backup your existing database
cp path/to/old/db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3

# Backup any custom configuration files
cp -r old_config_location config_backup/
```

### 2. **Update Repository**
```bash
# Pull latest changes from master
git checkout master
git pull origin master

# Install new dependencies
make setup  # Installs both Python and Node.js dependencies
```

### 3. **Configuration Migration**
```bash
# Create config directory
mkdir -p ./config

# Copy example settings
cp api/settings.yaml.example ./config/settings.yaml

# Copy environment template
cp .env.example .env
```

**Edit `./config/settings.yaml`** with your settings:
```yaml
# Key changes from previous version:
DATABASE:
  ENGINE: postgresql
  NAME: spotify_library_manager
  # ... other DB settings

CELERY:
  BROKER_URL: "sqlalchemy+postgresql://..."
  RESULT_BACKEND: "db+postgresql://..."

# Remove old Huey configuration completely
```

**Edit `.env`** for Docker:
```bash
# Database connection for containers
POSTGRES_DB=spotify_library_manager
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Volume paths
SLM_CONFIG_DIR=./config
MUSIC_DIR=./music
```

### 4. **Database Migration**

#### Option A: Fresh Start (Recommended for Development)
```bash
# Start with clean database
make dev-container

# Run migrations to create new schema
docker compose exec web python manage.py migrate

# Re-add your artists/playlists through the UI
```

#### Option B: Data Migration (Advanced)
```bash
# Export data from SQLite (if you have critical data)
# Note: Task history from Huey CANNOT be migrated to Celery (different systems)
python manage.py dumpdata library_manager.Artist library_manager.Album library_manager.Song library_manager.TrackedPlaylist --output=data_backup.json

# Start new system
make dev-container
docker compose exec web python manage.py migrate

# Load data into PostgreSQL
docker compose exec web python manage.py loaddata data_backup.json
```

**⚠️ Important Notes:**
- **Task History**: Previous Huey task history will be lost (incompatible systems)
- **Downloads**: Previously downloaded files remain untouched
- **Database Schema**: New Celery-specific tables will be created
- **Monitoring**: Task monitoring moves from Huey Monitor to Django Admin

### 5. **Development Workflow Update**

#### Old Workflow (No Longer Supported)
```bash
# ❌ Old way - mixed local/container setup
python manage.py runserver
huey_consumer.py app.huey  
cd frontend && npm start
```

#### New Workflow (Docker-First)
```bash
# ✅ New way - unified container development
make dev-container              # Start everything
make dev-container-logs         # View logs
make test-docker               # Run tests
make lint                      # Check code quality
```

## 🔧 **Key Differences**

### Task Management
| Aspect | Old (Huey) | New (Celery) |
|--------|------------|--------------|
| Broker | SQLite/Redis | PostgreSQL |
| Monitoring | Huey Monitor | Django Admin + Celery |
| Task IDs | Huey UUIDs | Celery UUIDs |
| Scheduling | Huey cron | Celery Beat |
| Results | SQLite table | PostgreSQL table |

### Development Environment  
| Aspect | Old | New |
|--------|-----|-----|
| Database | SQLite | PostgreSQL |
| Setup | Manual dependencies | `make dev-container` |
| Testing | Mixed environments | Docker containers |
| Linting | Manual commands | Integrated pipeline |

### Frontend Architecture
| Aspect | Old | New |
|--------|-----|-----|
| Routing | Legacy system | TanStack Router |
| Build | Basic Vite | Optimized Vite + Docker |
| Types | Manual GraphQL | Auto-generated |

## 🚨 **Troubleshooting Common Issues**

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker compose ps postgres

# View database logs
docker compose logs postgres

# Reset database if needed
docker compose down -v
docker compose up -d postgres
docker compose exec web python manage.py migrate
```

### Task Queue Not Working
```bash
# Check Celery worker status
docker compose logs worker

# Check Celery beat (scheduler)  
docker compose logs beat

# Restart task services
docker compose restart worker beat
```

### Frontend Build Issues
```bash
# Clear TanStack Router cache
rm -rf frontend/.tanstack frontend/dist

# Rebuild frontend
docker compose exec frontend yarn build

# Or restart frontend service
docker compose restart frontend
```

### Configuration Issues
```bash
# Validate settings
docker compose exec web python manage.py check

# View current configuration
docker compose exec web python -c "from django.conf import settings; print(settings.DATABASES)"
```

## 📋 **Migration Checklist**

- [ ] **Backup existing data** (database, config, music files)
- [ ] **Update repository** to latest branch
- [ ] **Install dependencies** with `make setup`
- [ ] **Configure settings** in `./config/settings.yaml`
- [ ] **Set environment variables** in `.env`
- [ ] **Start new system** with `make dev-container`
- [ ] **Run migrations** with `docker compose exec web python manage.py migrate`
- [ ] **Test functionality** (add artist, trigger download)
- [ ] **Verify task queue** working in Django admin
- [ ] **Update any scripts/automation** to use new commands

## 🎯 **Post-Migration Verification**

1. **Web Interface**: Visit http://localhost:3000
2. **API**: Check http://localhost:5000/graphql  
3. **Django Admin**: Check http://localhost:5000/admin (for task monitoring)
4. **Task Queue**: Add an artist and verify download tasks appear
5. **Logs**: Check `make dev-container-logs` for any errors

## 🔄 **Rollback Plan**

If you need to rollback to the previous system:

```bash
# Stop new system
make dev-container-down

# Restore backup database
cp db_backup_YYYYMMDD.sqlite3 path/to/old/db.sqlite3

# Checkout previous stable commit (before this overhaul)
git checkout <previous_working_commit_hash>

# Restart old system with previous commands
```

## 📞 **Getting Help**

- **Development Issues**: Check logs with `make dev-container-logs`
- **Database Issues**: Use `docker compose exec web python manage.py shell` for debugging
- **Task Queue**: Monitor tasks in Django admin interface
- **Build Issues**: Clear caches and restart: `docker compose down && make dev-container`

## 🎵 **What's New & Improved**

- **Reliability**: PostgreSQL replaces SQLite for production-grade reliability
- **Monitoring**: Full task visibility through Django admin
- **Development**: One-command setup with `make dev-container`
- **Type Safety**: Complete TypeScript + MyPy coverage  
- **Performance**: Optimized task processing with Celery
- **Scalability**: Production-ready architecture
- **Documentation**: Comprehensive contributor guides

The new system provides a much more robust foundation for development and production use!
