# Debugging Guide

This guide covers debugging worker crashes, performance issues, and other runtime problems in the Spotify Library Manager.

## Worker Diagnostics

The application includes comprehensive diagnostic logging to help debug worker crashes and performance issues.

### Enabling Diagnostics

Set `worker_diagnostics_enabled: true` in your `config/settings.yaml`:

```yaml
default:
  worker_diagnostics_enabled: true  # Enable for dev/debugging, disable for production
```

**Production recommendation**: Set to `false` to reduce log noise. Signal handlers (crash logging) remain active regardless.

### Diagnostic Features

**Signal Handlers** (`api/celery_app.py`):
- **Always active** (even when `worker_diagnostics_enabled: false`)
- Catches SIGTERM, SIGINT, and SIGQUIT signals before worker shutdown
- Logs process state (PID, memory usage, thread count) when signal received
- Logs active task information (task name, task ID) if available
- Helps identify WHY workers are killed (OOM, Docker restart, manual kill, etc.)

**Worker Lifecycle Logging** (`api/celery_app.py`):
- Requires `worker_diagnostics_enabled: true`
- Logs when worker processes start (PID, parent PID, initial memory)
- Logs when worker processes shut down (PID, final memory usage)
- Logs when main worker shuts down
- Helps identify restart patterns and process lifecycle issues

**Memory Monitoring** (`api/library_manager/tasks.py`):
- Requires `worker_diagnostics_enabled: true`
- Logs memory usage at task creation
- Logs memory usage at task completion (success or failure)
- Uses `psutil` to track RSS (Resident Set Size) and memory percentage
- Format: `[MEMORY] {context} - RSS: {mb} MB, Memory %: {percent}%, Task: {task_id}`

**Docker Memory Limits** (`docker-compose.yml`):
- **Worker container**: 2GB hard limit, 512MB soft limit (handles downloads)
- **Web container**: 1GB hard limit, 256MB soft limit (API server)
- **Beat container**: 512MB hard limit, 128MB soft limit (scheduler)
- Prevents system-wide OOM kills by containing memory usage
- Docker gracefully terminates containers that exceed limits

## Debugging Worker Crashes

When investigating worker crashes, follow these steps:

### 1. Check logs for SIGTERM signal

```bash
docker compose logs worker | grep "WORKER DIAGNOSTIC"
```

**Look for:**
- `Received SIGTERM` - Worker was killed
- `Active task:` - What task was running when killed
- `Memory RSS:` - Memory usage at time of kill
- `Memory %:` - Percentage of available memory

**Example output:**
```
[WORKER DIAGNOSTIC] Received SIGTERM (graceful shutdown requested) - PID: 16, Memory RSS: 1847.23 MB, Memory %: 92.36%, Threads: 4, Status: running
[WORKER DIAGNOSTIC] Active task: library_manager.tasks.download_playlist, Task ID: download-playlist-6efe475ab303
```

**Interpretation:**
- Worker hit 2GB memory limit (92% of 2GB ≈ 1.8GB)
- Was downloading a playlist when killed
- Docker sent SIGTERM due to OOM

### 2. Check memory usage patterns

```bash
docker compose logs worker | grep "MEMORY"
```

**Look for:**
- Memory growth over time (potential memory leak)
- Tasks that consume high memory
- Tasks that fail to release memory after completion

**Example output:**
```
[MEMORY] Task created: DOWNLOAD/PLAYLIST - RSS: 245.12 MB, Memory %: 12.26%, Task: download-playlist-abc123
[MEMORY] Task completed - RSS: 1234.56 MB, Memory %: 61.73%, Task: download-playlist-abc123
```

**Interpretation:**
- Task started at 245MB
- Ended at 1234MB
- Consumed ~1GB during execution (normal for large playlists)

### 3. Check Docker container status

```bash
docker compose ps                    # Container status
docker stats                         # Real-time resource usage (CPU, memory, I/O)
docker compose logs worker --tail 100  # Recent worker logs
```

### 4. Check for OOM kills in system logs (Linux)

```bash
dmesg | grep -i oom                  # Kernel OOM killer logs
journalctl -k | grep -i oom          # System journal OOM logs
```

## Common Crash Causes

### 1. Out of Memory (OOM)
**Symptom**: `SIGTERM` with high memory usage in logs (>90%)

**Diagnosis:**
```bash
docker compose logs worker | grep "WORKER DIAGNOSTIC"
# Look for high Memory % values (>80%)
```

**Fixes:**
- **Option A**: Increase worker memory limit in `docker-compose.yml`
  ```yaml
  worker:
    deploy:
      resources:
        limits:
          memory: 4G  # Increase from 2G to 4G
  ```
- **Option B**: Reduce worker concurrency
  ```yaml
  worker:
    command: celery -A celery_app worker --concurrency=5  # Reduce from 10
  ```
- **Option C**: Reduce download task rate limits in `api/celery_app.py`

### 2. Docker Health Check Failure
**Symptom**: Container restarts every ~90 seconds, clean shutdown logs

**Diagnosis:**
```bash
docker compose logs web | grep health
docker compose ps  # Look for "unhealthy" status
```

**Fixes:**
- Check web container logs for errors
- Verify health check endpoint responds: `curl http://localhost:5000/healthz`
- Increase health check timeout in `docker-compose.yml`

### 3. Manual Restart
**Symptom**: Clean shutdown with normal memory usage

**Diagnosis:**
```bash
docker compose logs worker | tail -50
# Look for graceful shutdown messages without high memory
```

**Context**: Check who/what triggered restart (CI/CD, manual `docker compose restart`, etc.)

### 4. Resource Starvation
**Symptom**: Slow task execution, timeouts, then SIGTERM

**Diagnosis:**
```bash
docker stats  # Check CPU, memory, disk I/O
htop          # System-wide resource usage
```

**Fixes:**
- Reduce concurrency to lower resource usage
- Add more system resources (CPU, RAM, disk space)
- Check for disk I/O bottlenecks (slow download destination)

## Performance Debugging

### Monitor Real-Time Resource Usage

```bash
# Watch container resource usage
docker stats

# Follow worker logs live
docker compose logs -f worker

# Filter for specific log types
docker compose logs -f worker | grep -E "MEMORY|WORKER DIAGNOSTIC"
```

### Identify Slow Tasks

```bash
# Check task execution times in database
docker compose exec web python manage.py shell
>>> from library_manager.models import TaskHistory
>>> slow_tasks = TaskHistory.objects.filter(duration_seconds__gt=300).order_by('-duration_seconds')[:10]
>>> for task in slow_tasks:
...     print(f"{task.type} {task.entity_id}: {task.duration_seconds}s")
```

### Profile Download Performance

Enable verbose logging in `config/settings.yaml`:

```yaml
default:
  log_level: "DEBUG"
  worker_diagnostics_enabled: true
```

Then monitor download progress:

```bash
docker compose logs -f worker | grep -E "Downloading|MEMORY"
```

## Advanced Debugging

### Attach to Running Worker

```bash
# Get worker container ID
docker compose ps worker

# Attach to worker process
docker compose exec worker bash

# Inside container, check process status
ps aux | grep celery
top -p <worker_pid>
```

### Check Database for Stuck Tasks

```bash
docker compose exec web python manage.py shell
>>> from library_manager.models import TaskHistory
>>> from django.utils import timezone
>>> from datetime import timedelta
>>>
>>> # Find tasks stuck in RUNNING for >1 hour
>>> stuck = TaskHistory.objects.filter(
...     status='RUNNING',
...     started_at__lt=timezone.now() - timedelta(hours=1)
... )
>>> for task in stuck:
...     print(f"{task.task_id}: {task.type} - {task.started_at}")
```

### Enable Python Memory Profiling

For deep memory analysis, install `memory_profiler`:

```bash
docker compose exec worker pip install memory_profiler
```

Then profile specific tasks by decorating them with `@profile` (requires code changes).

## Troubleshooting Checklist

- [ ] Check worker logs for SIGTERM with memory usage
- [ ] Check if memory usage is growing over time
- [ ] Verify Docker memory limits are appropriate
- [ ] Check if worker concurrency is too high
- [ ] Verify system has enough resources (RAM, CPU, disk)
- [ ] Check for disk I/O bottlenecks (slow storage)
- [ ] Verify YouTube Music cookies are valid (for downloads)
- [ ] Check Spotify API credentials are working (for metadata)
- [ ] Look for stuck tasks in database
- [ ] Check for network issues (slow downloads, API timeouts)

## Getting Help

If you're still stuck:

1. **Collect diagnostic logs**: `docker compose logs worker > worker.log`
2. **Check system resources**: `docker stats > stats.txt`
3. **Export recent task history**: Query `TaskHistory` table for failed tasks
4. **Document the issue**: What were you doing when it crashed? Is it reproducible?
5. **File an issue**: Include logs, stats, and reproduction steps
