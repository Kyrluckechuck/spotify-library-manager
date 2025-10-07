/**
 * Entity display configuration
 * Maps entity types and task types to their visual representation
 */

interface EntityDisplayConfig {
  icon: string;
  label: string;
  color: string;
}

type EntityType = 'ARTIST' | 'ALBUM' | 'PLAYLIST' | 'TRACK';
type TaskType = 'FETCH' | 'SYNC' | 'DOWNLOAD';

// Base entity icons and colors (used when no task type is specified)
export const ENTITY_ICONS: Record<EntityType, EntityDisplayConfig> = {
  ARTIST: { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' },
  ALBUM: { icon: '💿', label: 'ALBUM', color: 'text-purple-600' },
  PLAYLIST: { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' },
  TRACK: { icon: '🎵', label: 'TRACK', color: 'text-orange-600' },
};

// Task-specific icons override base icons
export const TASK_ICONS: Record<
  TaskType,
  Partial<Record<EntityType, EntityDisplayConfig>>
> = {
  FETCH: {
    ARTIST: { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' },
    ALBUM: { icon: '💿', label: 'ALBUM', color: 'text-purple-600' },
    PLAYLIST: { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' },
  },
  SYNC: {
    ARTIST: { icon: '🔄', label: 'ARTIST', color: 'text-blue-600' },
    PLAYLIST: { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' },
    ALBUM: { icon: '💿', label: 'ALBUM', color: 'text-purple-600' },
  },
  DOWNLOAD: {
    ARTIST: { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' },
    PLAYLIST: { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' },
    ALBUM: { icon: '💿', label: 'ALBUM', color: 'text-purple-600' },
    TRACK: { icon: '🎵', label: 'TRACK', color: 'text-orange-600' },
  },
};

/**
 * Get entity display configuration based on entity type and optional task type
 */
export function getEntityDisplayConfig(
  entityType: string,
  taskType?: string
): EntityDisplayConfig {
  const upperEntity = entityType.toUpperCase() as EntityType;
  const upperTask = taskType?.toUpperCase() as TaskType | undefined;

  // If task type is specified, try to get task-specific icon
  if (upperTask) {
    const taskConfig = TASK_ICONS[upperTask]?.[upperEntity];
    if (taskConfig) {
      return taskConfig;
    }
  }

  // Fall back to base entity icon
  if (ENTITY_ICONS[upperEntity]) {
    return ENTITY_ICONS[upperEntity];
  }

  // Ultimate fallback for unknown types
  return {
    icon: '❓',
    label: upperEntity || 'UNKNOWN',
    color: 'text-gray-600',
  };
}
