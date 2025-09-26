import React, { useEffect, useState } from 'react';
import {
  useGetArtistQuery,
  useGetSongLazyQuery,
} from '../types/generated/graphql';

interface EnhancedEntityDisplayProps {
  entityType: string;
  entityId: string;
  taskType?: string;
  compact?: boolean;
}

interface EntityData {
  id: string;
  name: string;
  url?: string;
  gid?: string;
  primaryArtist?: string;
}

const EnhancedEntityDisplay: React.FC<EnhancedEntityDisplayProps> = ({
  entityType,
  entityId,
  taskType,
  compact = false,
}) => {
  const [entityData, setEntityData] = useState<EntityData | null>(null);

  // Helper function to determine if entity ID is a Spotify URL
  const isSpotifyUrl = (id: string): boolean => {
    return (
      id.startsWith('//open.spotify.com/') ||
      id.startsWith('https://open.spotify.com/')
    );
  };

  // Helper function to determine if entity ID is a test name
  const isTestName = (id: string): boolean => {
    return id.startsWith('test-');
  };

  // Helper function to determine if entity ID should be skipped for GraphQL queries
  const shouldSkipGraphQL = (id: string): boolean => {
    // Only skip GraphQL for truly problematic formats:
    // 1. Full Spotify URLs
    // 2. Test names
    // Note: Numeric IDs are now handled by the backend services
    return isSpotifyUrl(id) || isTestName(id);
  };

  const shouldSkip = shouldSkipGraphQL(entityId);
  const upperEntityType = entityType.toUpperCase();

  // Use typed hooks based on entity type
  const artistQuery = useGetArtistQuery({
    variables: { id: entityId },
    skip: shouldSkip || upperEntityType !== 'ARTIST',
    fetchPolicy: 'cache-first',
    errorPolicy: 'ignore',
  });

  // Album and playlist queries are not available as single entity queries
  // So we'll skip GraphQL fetching for these types and use fallback display
  const albumQuery = { data: undefined, loading: false };
  const playlistQuery = { data: undefined, loading: false };

  const [getSong, songQuery] = useGetSongLazyQuery({
    fetchPolicy: 'cache-first',
    errorPolicy: 'ignore',
  });

  // Trigger song query when needed
  useEffect(() => {
    if (!shouldSkip && upperEntityType === 'TRACK') {
      getSong({ variables: { id: entityId } });
    }
  }, [entityId, shouldSkip, upperEntityType, getSong]);

  // Determine which query result to use
  const activeQuery =
    upperEntityType === 'ARTIST'
      ? artistQuery
      : upperEntityType === 'ALBUM'
        ? albumQuery
        : upperEntityType === 'PLAYLIST'
          ? playlistQuery
          : upperEntityType === 'TRACK'
            ? songQuery
            : { data: undefined, loading: false };

  const { data, loading } = activeQuery;

  useEffect(() => {
    if (data) {
      let entity: EntityData | null = null;

      if (upperEntityType === 'ARTIST' && artistQuery.data?.artist) {
        entity = {
          id: artistQuery.data.artist.id.toString(),
          name: artistQuery.data.artist.name,
          gid: artistQuery.data.artist.gid,
        };
      } else if (upperEntityType === 'TRACK' && songQuery.data?.song) {
        entity = {
          id: songQuery.data.song.id.toString(),
          name: songQuery.data.song.name,
          gid: songQuery.data.song.gid,
          primaryArtist: songQuery.data.song.primaryArtist,
        };
      }
      // Note: Album and playlist queries are not available as single entity queries
      // so we rely on fallback display for these entity types

      setEntityData(entity);
    }
  }, [data, upperEntityType, artistQuery.data, songQuery.data]);

  // Helper function to get the appropriate icon and color based on entity type and task type
  const getEntityDisplay = () => {
    const baseEntity = entityType.toUpperCase();

    // Handle different task types with appropriate icons
    if (taskType) {
      const task = taskType.toUpperCase();

      switch (task) {
        case 'FETCH':
          switch (baseEntity) {
            case 'ARTIST':
              return { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' };
            case 'ALBUM':
              return { icon: '💿', label: 'ALBUM', color: 'text-purple-600' };
            case 'PLAYLIST':
              return { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' };
            default:
              return { icon: '🔍', label: baseEntity, color: 'text-gray-600' };
          }

        case 'SYNC':
          switch (baseEntity) {
            case 'ARTIST':
              return { icon: '🔄', label: 'ARTIST', color: 'text-blue-600' };
            case 'PLAYLIST':
              return { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' };
            case 'ALBUM':
              return { icon: '💿', label: 'ALBUM', color: 'text-purple-600' };
            default:
              return { icon: '🔄', label: baseEntity, color: 'text-gray-600' };
          }

        case 'DOWNLOAD':
          switch (baseEntity) {
            case 'ARTIST':
              return { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' };
            case 'PLAYLIST':
              return { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' };
            case 'ALBUM':
              return { icon: '💿', label: 'ALBUM', color: 'text-purple-600' };
            case 'TRACK':
              return { icon: '🎵', label: 'TRACK', color: 'text-orange-600' };
            default:
              return { icon: '⬇️', label: baseEntity, color: 'text-gray-600' };
          }

        default:
          // Fallback for unknown task types
          switch (baseEntity) {
            case 'ARTIST':
              return { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' };
            case 'PLAYLIST':
              return { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' };
            case 'ALBUM':
              return { icon: '💿', label: 'ALBUM', color: 'text-purple-600' };
            case 'TRACK':
              return { icon: '🎵', label: 'TRACK', color: 'text-orange-600' };
            default:
              return { icon: '❓', label: baseEntity, color: 'text-gray-600' };
          }
      }
    }

    // Fallback for when no task type is provided
    switch (baseEntity) {
      case 'ARTIST':
        return { icon: '🎤', label: 'ARTIST', color: 'text-blue-600' };
      case 'PLAYLIST':
        return { icon: '📜', label: 'PLAYLIST', color: 'text-green-600' };
      case 'ALBUM':
        return { icon: '💿', label: 'ALBUM', color: 'text-purple-600' };
      case 'TRACK':
        return { icon: '🎵', label: 'TRACK', color: 'text-orange-600' };
      default:
        return { icon: '❓', label: baseEntity, color: 'text-gray-600' };
    }
  };

  // Helper function to create display name for special entity ID formats
  const getSpecialEntityDisplay = (): { name: string; url?: string } | null => {
    if (isSpotifyUrl(entityId)) {
      // Extract playlist ID from Spotify URL
      const playlistIdMatch = entityId.match(/playlist\/([a-zA-Z0-9]+)/);
      const playlistId = playlistIdMatch ? playlistIdMatch[1] : entityId;
      return {
        name: `Playlist ${playlistId}`,
        url: entityId.startsWith('//') ? `https:${entityId}` : entityId,
      };
    }

    if (isTestName(entityId)) {
      return {
        name: entityId.replace('test-', 'Test Playlist '),
        url: undefined,
      };
    }

    return null;
  };

  const { icon, label, color } = getEntityDisplay();
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

      if (specialEntity.url) {
        return (
          <div className='flex items-center space-x-1 min-w-0 w-full'>
            <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
            <a
              href={specialEntity.url}
              target='_blank'
              rel='noopener noreferrer'
              className='text-blue-600 hover:text-blue-800 hover:underline text-xs truncate flex-1 min-w-0'
              title={`View ${entityType.toLowerCase()}: ${specialEntity.name}`}
            >
              {displayName}
            </a>
            <span className='text-gray-500 text-xs flex-shrink-0'>
              ({label})
            </span>
          </div>
        );
      } else {
        return (
          <div className='flex items-center space-x-1 min-w-0 w-full'>
            <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
            <span
              className='text-xs text-gray-900 truncate flex-1 min-w-0 font-medium'
              title={specialEntity.name}
            >
              {displayName}
            </span>
            <span className='text-gray-500 text-xs flex-shrink-0'>
              ({label})
            </span>
          </div>
        );
      }
    } else {
      // Full mode for special entities
      if (specialEntity.url) {
        return (
          <div className='flex items-center space-x-2'>
            <span className={`text-lg ${color}`}>{icon}</span>
            <a
              href={specialEntity.url}
              target='_blank'
              rel='noopener noreferrer'
              className='text-blue-600 hover:text-blue-800 hover:underline font-medium'
              title={`View ${entityType.toLowerCase()}: ${specialEntity.name}`}
            >
              {specialEntity.name}
            </a>
            <span className='text-gray-500 text-xs'>({label})</span>
          </div>
        );
      } else {
        return (
          <div className='flex items-center space-x-2'>
            <span className={`text-lg ${color}`}>{icon}</span>
            <span className='font-medium text-gray-900'>
              {specialEntity.name}
            </span>
            <span className='text-gray-500 text-xs'>({label})</span>
          </div>
        );
      }
    }
  }

  // If we have entity data, display it with the real name
  if (entityData) {
    if (compact) {
      // Compact mode for table display
      const displayName =
        entityData.name.length > 20
          ? `${entityData.name.substring(0, 20)}...`
          : entityData.name;

      if (entityLink) {
        return (
          <div className='flex items-center space-x-1 min-w-0 w-full'>
            <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
            <a
              href={entityLink}
              target='_blank'
              rel='noopener noreferrer'
              className='text-blue-600 hover:text-blue-800 hover:underline text-xs truncate flex-1 min-w-0'
              title={`View ${entityType.toLowerCase()}: ${entityData.name}`}
            >
              {displayName}
            </a>
            <span className='text-gray-500 text-xs flex-shrink-0'>
              ({label})
            </span>
          </div>
        );
      } else {
        return (
          <div className='flex items-center space-x-1 min-w-0 w-full'>
            <span className={`text-sm flex-shrink-0 ${color}`}>{icon}</span>
            <span
              className='text-xs text-gray-900 truncate flex-1 min-w-0 font-medium'
              title={entityData.name}
            >
              {displayName}
            </span>
            <span className='text-gray-500 text-xs flex-shrink-0'>
              ({label})
            </span>
          </div>
        );
      }
    } else {
      // Full mode for other displays
      if (entityLink) {
        return (
          <div className='flex items-center space-x-2'>
            <span className={`text-lg ${color}`}>{icon}</span>
            <a
              href={entityLink}
              target='_blank'
              rel='noopener noreferrer'
              className='text-blue-600 hover:text-blue-800 hover:underline font-medium'
              title={`View ${entityType.toLowerCase()}: ${entityData.name}`}
            >
              {entityData.name}
            </a>
            <span className='text-gray-500 text-xs'>({label})</span>
          </div>
        );
      } else {
        return (
          <div className='flex items-center space-x-2'>
            <span className={`text-lg ${color}`}>{icon}</span>
            <span className='font-medium text-gray-900'>{entityData.name}</span>
            <span className='text-gray-500 text-xs'>({label})</span>
          </div>
        );
      }
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
