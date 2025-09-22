import React, { useEffect, useState } from 'react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';

// GraphQL queries for fetching entity details
const GET_ARTIST = gql`
  query GetArtistForDisplay($id: String!) {
    artist(id: $id) {
      id
      name
      gid
    }
  }
`;

const GET_ALBUM = gql`
  query GetAlbum($id: String!) {
    album(id: $id) {
      id
      name
      spotifyGid
    }
  }
`;

const GET_PLAYLIST = gql`
  query GetPlaylist($id: String!) {
    playlist(id: $id) {
      id
      name
      url
    }
  }
`;

const GET_SONG = gql`
  query GetSongForDisplay($id: String!) {
    song(id: $id) {
      id
      name
      gid
      primaryArtist
    }
  }
`;

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

  // Determine which query to use based on entity type and ID format
  const getQueryAndVariables = () => {
    const upperEntityType = entityType.toUpperCase();

    // Skip GraphQL queries for certain ID formats that won't work
    if (shouldSkipGraphQL(entityId)) {
      return null;
    }

    switch (upperEntityType) {
      case 'ARTIST':
        return { query: GET_ARTIST, variables: { id: entityId } };
      case 'ALBUM':
        return { query: GET_ALBUM, variables: { id: entityId } };
      case 'PLAYLIST':
        return { query: GET_PLAYLIST, variables: { id: entityId } };
      case 'TRACK':
        return { query: GET_SONG, variables: { id: entityId } };
      default:
        return null;
    }
  };

  const queryConfig = getQueryAndVariables();

  // Use the appropriate query if available
  const { data, loading } = useQuery(queryConfig?.query || GET_ARTIST, {
    variables: queryConfig?.variables || { id: entityId },
    skip: !queryConfig,
    fetchPolicy: 'cache-first',
    errorPolicy: 'ignore', // Don't show errors for ID format mismatches
  });

  useEffect(() => {
    if (data) {
      let entity: EntityData | null = null;

      if (data.artist) {
        entity = {
          id: data.artist.id,
          name: data.artist.name,
          gid: data.artist.gid,
        };
      } else if (data.album) {
        entity = {
          id: data.album.id,
          name: data.album.name,
          gid: data.album.spotifyGid,
        };
      } else if (data.playlist) {
        entity = {
          id: data.playlist.id,
          name: data.playlist.name,
          url: data.playlist.url,
        };
      } else if (data.song) {
        entity = {
          id: data.song.id,
          name: data.song.name,
          gid: data.song.gid,
          primaryArtist: data.song.primaryArtist,
        };
      }

      setEntityData(entity);
    }
  }, [data]);

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
