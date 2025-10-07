import { useEffect, useState } from 'react';
import { useQuery, useLazyQuery } from '@apollo/client/react';
import { GetArtistDocument, GetSongDocument } from '../types/generated/graphql';

export interface EntityData {
  id: string;
  name: string;
  url?: string;
  gid?: string;
  primaryArtist?: string;
}

/**
 * Hook to fetch entity data based on entity type and ID
 * Handles GraphQL queries for artists and songs, with fallback for albums/playlists
 */
export function useEntityData(entityType: string, entityId: string) {
  const [entityData, setEntityData] = useState<EntityData | null>(null);

  // Helper functions
  const isSpotifyUrl = (id: string): boolean => {
    return (
      id.startsWith('//open.spotify.com/') ||
      id.startsWith('https://open.spotify.com/')
    );
  };

  const isTestName = (id: string): boolean => {
    return id.startsWith('test-');
  };

  const shouldSkipGraphQL = (id: string): boolean => {
    // Skip GraphQL for Spotify URLs and test names
    return isSpotifyUrl(id) || isTestName(id);
  };

  const shouldSkip = shouldSkipGraphQL(entityId);
  const upperEntityType = entityType.toUpperCase();

  // Artist query
  const artistQuery = useQuery(GetArtistDocument, {
    variables: { id: entityId },
    skip: shouldSkip || upperEntityType !== 'ARTIST',
    fetchPolicy: 'cache-first',
    errorPolicy: 'ignore',
  });

  // Song query (lazy - triggered by effect)
  const [getSong, songQuery] = useLazyQuery(GetSongDocument, {
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
      : upperEntityType === 'TRACK'
        ? songQuery
        : { data: undefined, loading: false };

  const { data, loading } = activeQuery;

  // Extract entity data from query results
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

      setEntityData(entity);
    }
  }, [data, upperEntityType, artistQuery.data, songQuery.data]);

  return {
    entityData,
    loading,
    isSpotifyUrl: isSpotifyUrl(entityId),
    isTestName: isTestName(entityId),
  };
}
