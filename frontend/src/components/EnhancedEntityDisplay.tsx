import React from 'react';
import { useEntityData } from '../hooks/useEntityData';
import { getEntityDisplayConfig } from './entity-display/entityConfig';
import { CompactEntityDisplay } from './entity-display/CompactEntityDisplay';
import { FullEntityDisplay } from './entity-display/FullEntityDisplay';

interface EnhancedEntityDisplayProps {
  entityType: string;
  entityId: string;
  taskType?: string;
  compact?: boolean;
}

const EnhancedEntityDisplay: React.FC<EnhancedEntityDisplayProps> = ({
  entityType,
  entityId,
  taskType,
  compact = false,
}) => {
  const { entityData, loading, isSpotifyUrl, isTestName } = useEntityData(
    entityType,
    entityId
  );

  // Get display configuration from centralized config
  const { icon, label, color } = getEntityDisplayConfig(entityType, taskType);

  // Helper function to create display name for special entity ID formats
  const getSpecialEntityDisplay = (): { name: string; url?: string } | null => {
    if (isSpotifyUrl) {
      // Extract playlist ID from Spotify URL
      const playlistIdMatch = entityId.match(/playlist\/([a-zA-Z0-9]+)/);
      const playlistId = playlistIdMatch ? playlistIdMatch[1] : entityId;
      return {
        name: `Playlist ${playlistId}`,
        url: entityId.startsWith('//') ? `https:${entityId}` : entityId,
      };
    }

    if (isTestName) {
      return {
        name: entityId.replace('test-', 'Test Playlist '),
        url: undefined,
      };
    }

    return null;
  };
  const entityLink = entityData?.url;
  const specialEntity = getSpecialEntityDisplay();

  // Handle loading state
  if (loading) {
    return (
      <div className='flex items-center space-x-1 min-w-0 w-full'>
        <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
        <div className='w-16 h-3 bg-gray-200 rounded animate-pulse flex-1' />
        <span className='text-gray-500 text-xs flex-shrink-0'>({label})</span>
      </div>
    );
  }

  // If we have special entity display (for non-GraphQL entities), use that
  if (specialEntity) {
    if (compact) {
      const displayName =
        specialEntity.name.length > 20
          ? `${specialEntity.name.substring(0, 20)}...`
          : specialEntity.name;

      return (
        <CompactEntityDisplay
          icon={icon}
          color={color}
          displayName={displayName}
          fullName={specialEntity.name}
          label={label}
          entityType={entityType}
          link={specialEntity.url}
        />
      );
    } else {
      return (
        <FullEntityDisplay
          icon={icon}
          color={color}
          name={specialEntity.name}
          label={label}
          entityType={entityType}
          link={specialEntity.url}
        />
      );
    }
  }

  // If we have entity data, display it with the real name
  if (entityData) {
    if (compact) {
      const displayName =
        entityData.name.length > 20
          ? `${entityData.name.substring(0, 20)}...`
          : entityData.name;

      return (
        <CompactEntityDisplay
          icon={icon}
          color={color}
          displayName={displayName}
          fullName={entityData.name}
          label={label}
          entityType={entityType}
          link={entityLink}
        />
      );
    } else {
      return (
        <FullEntityDisplay
          icon={icon}
          color={color}
          name={entityData.name}
          label={label}
          entityType={entityType}
          link={entityLink}
        />
      );
    }
  }

  // Fallback to original display if no data or error
  if (compact) {
    // Compact fallback - show truncated entity ID
    const fallbackText =
      entityId.length > 15
        ? `${label} ${entityId.substring(0, 15)}...`
        : `${label} ${entityId}`;

    return (
      <div className='flex items-center space-x-1 min-w-0 w-full'>
        <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
        <span
          className='text-xs text-gray-500 truncate flex-1 min-w-0'
          title={entityId}
        >
          {fallbackText}
        </span>
        <span className='text-gray-500 text-xs flex-shrink-0'>({label})</span>
      </div>
    );
  } else {
    // Full fallback
    return (
      <div className='flex items-center space-x-2'>
        <span className={`text-lg ${color}`}>{icon}</span>
        <span className='text-gray-700'>
          {label} {entityId}
        </span>
      </div>
    );
  }
};

export default EnhancedEntityDisplay;
