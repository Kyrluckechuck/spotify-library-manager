# PostgreSQL Migration Plan

## Overview & Rationale

**Current State**: SQLite database with Huey SQLite backend
**Target State**: PostgreSQL database with Huey PostgreSQL backend
**Primary Goal**: Solve database locking issues and improve concurrent access

**Why PostgreSQL Now**:
- Database locking issues with current SQLite setup
- Already doing major app overhaul - perfect timing for infrastructure changes
- Better concurrent access handling for multiple workers
- Industry standard for production applications
- Single database for both app and task queue (cleaner architecture)

**Benefits**:
- Eliminates "database is locked" errors
- Better performance with concurrent operations
- Cleaner table names (removing `library_manager_` prefix)
- More robust for production use
- Better tooling and monitoring support

## Pre-Migration Checklist

- [ ] Backup current SQLite database
- [ ] Ensure all current work is committed
- [ ] Plan maintenance window if needed
- [ ] Verify Docker environment is ready
- [ ] Test migration process in development environment

## Implementation Steps

### Phase 1: Infrastructure Setup
- [ ] Add PostgreSQL service to docker-compose.yml
- [ ] Update Django settings for PostgreSQL backend
- [ ] Configure Huey to use PostgreSQL backend
- [ ] Update requirements.txt with PostgreSQL dependencies
- [ ] Test PostgreSQL connection and basic functionality

### Phase 2: Table Naming Cleanup
- [ ] Update Django models with clean table names
- [ ] Remove `library_manager_` prefix from all tables
- [ ] Verify table naming conventions are consistent
- [ ] Test model operations with new table names

### Phase 3: Auto-Migration Logic
- [ ] Create Django management command for auto-migration
- [ ] Implement startup detection for empty PostgreSQL
- [ ] Create data migration script from SQLite to PostgreSQL
- [ ] Test migration process end-to-end
- [ ] Add rollback capabilities

### Phase 4: Testing & Validation
- [ ] Test all application functionality with PostgreSQL
- [ ] Verify Huey tasks work correctly
- [ ] Performance testing and comparison
- [ ] Data integrity verification
- [ ] Rollback testing

## Configuration Changes

### Docker Compose Updates
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: spotify_library_manager
      POSTGRES_USER: slm_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-slm_dev_password}
    volumes:
      - config_storage:/config/db/postgresql
    networks:
      - slm_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U slm_user -d spotify_library_manager"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Django Settings Updates
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "spotify_library_manager"),
        "USER": os.getenv("POSTGRES_USER", "slm_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "slm_dev_password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

HUEY = {
    "huey_class": "huey.PostgresqlHuey",
    "name": "spotify_library_manager",
    "url": f"postgresql://{os.getenv('POSTGRES_USER', 'slm_user')}:{os.getenv('POSTGRES_PASSWORD', 'slm_dev_password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'spotify_library_manager')}",
    "immediate": False,
    "results": True,
    "store_none": False,
}
```

### Model Table Name Updates
```python
class Album(models.Model):
    class Meta:
        db_table = 'albums'  # Instead of library_manager_album

class Artist(models.Model):
    class Meta:
        db_table = 'artists'  # Instead of library_manager_artist

class Song(models.Model):
    class Meta:
        db_table = 'songs'  # Instead of library_manager_song

class TrackedPlaylist(models.Model):
    class Meta:
        db_table = 'playlists'  # Instead of library_manager_trackedplaylist

class TaskHistory(models.Model):
    class Meta:
        db_table = 'task_history'  # Instead of library_manager_taskhistory

class DownloadHistory(models.Model):
    class Meta:
        db_table = 'download_history'  # Instead of library_manager_downloadhistory
```

## Dependencies to Add
```
psycopg2-binary>=2.9.0
huey[postgresql]>=2.5.0
```

## Testing & Validation

### Functional Testing
- [ ] All GraphQL queries work correctly
- [ ] All mutations (create, update, delete) function properly
- [ ] Background tasks execute successfully
- [ ] File downloads and processing work
- [ ] User authentication and sessions work
- [ ] API endpoints respond correctly

### Performance Testing
- [ ] Database query performance comparison
- [ ] Concurrent user access testing
- [ ] Background task throughput
- [ ] Memory usage comparison
- [ ] Startup time comparison

### Data Integrity
- [ ] All existing data migrated correctly
- [ ] No data loss during migration
- [ ] Foreign key relationships maintained
- [ ] Indexes and constraints preserved
- [ ] Task history and download history intact

## Rollback Plan

### Quick Rollback (if issues detected immediately)
1. Stop PostgreSQL services
2. Revert docker-compose.yml to previous version
3. Restart with SQLite backend
4. Verify all functionality restored

### Full Rollback (if issues persist)
1. Restore SQLite database from backup
2. Revert all code changes
3. Restart services with original configuration
4. Verify complete functionality restoration

### Rollback Triggers
- Data corruption detected
- Performance degradation
- Critical functionality broken
- Migration process fails

## Post-Migration Tasks

- [ ] Monitor system performance for 24-48 hours
- [ ] Verify all scheduled tasks execute correctly
- [ ] Check error logs for any new issues
- [ ] Update documentation and deployment guides
- [ ] Remove old SQLite files (after verification period)
- [ ] Update backup procedures for PostgreSQL

## Environment Variables

### Required Environment Variables
```bash
POSTGRES_DB=spotify_library_manager
POSTGRES_USER=slm_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

### Optional Overrides
- Can override any PostgreSQL connection parameter via environment variables
- Defaults provided for development convenience
- Production should always set secure passwords

## Migration Commands

### Development Migration
```bash
# Stop current services
docker-compose down

# Start with new PostgreSQL setup
docker-compose up -d

# Monitor logs for auto-migration
docker-compose logs -f web
```

### Production Migration
```bash
# Deploy updated docker-compose.yml to Dockge
# Set environment variables in Dockge UI
# Deploy stack - auto-migration will handle the rest
# Monitor logs for migration completion
```

## Notes

- **Auto-migration**: System detects empty PostgreSQL and automatically migrates from SQLite
- **Clean cutover**: No dual-database support during transition
- **Volume reuse**: PostgreSQL data stored in `/config/db/postgresql/` alongside existing structure
- **Dockge compatible**: Works seamlessly with current deployment setup
- **No data loss**: Full migration with verification steps

## Success Criteria

- [ ] All existing functionality works with PostgreSQL
- [ ] No database locking errors occur
- [ ] Background tasks execute reliably
- [ ] Performance is at least equivalent to SQLite
- [ ] All data migrated successfully
- [ ] Clean table names implemented
- [ ] System stable for 24+ hours post-migration
