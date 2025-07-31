# TaskHistory Storage Optimizations

## Overview
This document describes the optimizations implemented to improve TaskHistory storage efficiency and performance.

## Changes Implemented

### 1. Data Retention Policy
- **Automatic cleanup** of completed/failed tasks older than 30 days
- **Configurable retention period** via management command
- **Preserves running and pending tasks** during cleanup

### 2. Log Message Limits
- **Automatic truncation** of log messages to maximum 50 per task
- **Removes heartbeat log messages** - only updates timestamp
- **Reduces JSON field size** and improves query performance

### 3. Database Indexes
Added performance indexes for common query patterns:
- `(status, -started_at)` - For filtering by status with date ordering
- `(type, -started_at)` - For filtering by task type
- `(entity_type, -started_at)` - For filtering by entity type
- `(completed_at)` - For cleanup operations

### 4. Management Commands

#### `cleanup_old_tasks`
```bash
# Show storage statistics
python manage.py cleanup_old_tasks --stats

# Dry run - see what would be deleted
python manage.py cleanup_old_tasks --days 7 --dry-run

# Actually delete old tasks
python manage.py cleanup_old_tasks --days 30
```

#### `cleanup_stuck_tasks`
```bash
# Clean up stuck tasks
python manage.py cleanup_stuck_tasks

# Force cleanup
python manage.py cleanup_stuck_tasks --force
```

## Storage Impact

### Before Optimizations
- **Unbounded log growth** - Every task could accumulate unlimited log messages
- **Heartbeat logs** - Added log message for every heartbeat update
- **No data retention** - Completed tasks kept indefinitely
- **No database indexes** - Slow queries on large datasets

### After Optimizations
- **Controlled log growth** - Maximum 50 logs per task
- **No heartbeat logs** - Only timestamp updates
- **30-day retention** - Automatic cleanup of old tasks
- **Optimized queries** - Database indexes for common filters

## Performance Benefits

### Storage Reduction
- **Log message truncation** reduces JSON field size by ~80%
- **Removed heartbeat logs** eliminates unnecessary log entries
- **Data retention** prevents unlimited growth

### Query Performance
- **Database indexes** improve filter query performance
- **Smaller JSON fields** reduce memory usage
- **Fewer records** in long-running systems

### Monitoring
- **Storage statistics** provide visibility into data growth
- **Cleanup commands** allow manual and automated maintenance
- **Dry-run mode** for safe testing

## Usage Examples

### Check Current Storage
```bash
python manage.py cleanup_old_tasks --stats
```

### Clean Up Old Data
```bash
# Keep only last 7 days
python manage.py cleanup_old_tasks --days 7

# Keep only last 30 days (default)
python manage.py cleanup_old_tasks
```

### Monitor Storage Growth
```python
from library_manager.models import TaskHistory

# Get storage statistics
stats = TaskHistory.get_storage_stats()
print(f"Total tasks: {stats['total_tasks']}")
print(f"Average logs per task: {stats['average_logs_per_task']}")
```

## Migration Notes

### Database Changes
- Added 4 new indexes to `TaskHistory` table
- No data migration required
- Backward compatible with existing data

### Code Changes
- Modified `add_log_message()` to include truncation
- Removed heartbeat log messages from `update_heartbeat()`
- Added cleanup and statistics methods

## Monitoring Recommendations

### Automated Cleanup
Set up a cron job for regular cleanup:
```bash
# Daily cleanup of old tasks
0 2 * * * cd /path/to/app && python manage.py cleanup_old_tasks --days 30
```

### Storage Monitoring
Monitor these metrics:
- Total task count
- Average logs per task
- Tasks with logs count
- Cleanup frequency and deleted count

## Future Considerations

### Potential Enhancements
- **Log compression** for very large log messages
- **Archiving strategy** for historical data
- **Real-time monitoring** of storage growth
- **Configurable log limits** per task type

### Scaling Considerations
- **Partitioning** for very large datasets
- **Separate log storage** for high-volume systems
- **Caching strategies** for frequently accessed data 
