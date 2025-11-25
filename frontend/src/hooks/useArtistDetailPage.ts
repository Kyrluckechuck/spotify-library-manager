import { useState, useMemo, useCallback } from 'react';
import { useMutation, useQuery } from '@apollo/client/react';
import {
  GetArtistDocument,
  GetAlbumsDocument,
  GetSongsDocument,
  TrackArtistDocument,
  UntrackArtistDocument,
  SyncArtistDocument,
  DownloadArtistDocument,
  SetAlbumWantedDocument,
  DownloadAlbumDocument,
  type Album,
  type Song,
} from '../types/generated/graphql';
import { useToast } from '../components/ui/useToast';
import { useMutationState, useMutationLoadingState } from './useMutationState';
import { useRequestState } from './useRequestState';
import type { AlbumSortField } from '../components/albums/AlbumsTable';
import type { SortField as SongSortField } from '../components/songs/SongsTable';
import type {
  SortDirection,
  WantedFilter,
  DownloadFilter,
} from '../types/shared';

interface UseArtistDetailPageOptions {
  artistId: string;
}

export function useArtistDetailPage({ artistId }: UseArtistDetailPageOptions) {
  const toast = useToast();

  // Albums state
  const [albumWantedFilter, setAlbumWantedFilter] =
    useState<WantedFilter>('all');
  const [albumDownloadFilter, setAlbumDownloadFilter] =
    useState<DownloadFilter>('all');
  const [albumPageSize, setAlbumPageSize] = useState(50);
  const [albumSortField, setAlbumSortField] = useState<AlbumSortField>(null);
  const [albumSortDirection, setAlbumSortDirection] =
    useState<SortDirection>('asc');
  const [albumSearchQuery, setAlbumSearchQuery] = useState('');

  // Songs state
  const [songDownloadFilter, setSongDownloadFilter] =
    useState<DownloadFilter>('all');
  const [songPageSize, setSongPageSize] = useState(50);
  const [songSortField, setSongSortField] = useState<SongSortField>(null);
  const [songSortDirection, setSongSortDirection] =
    useState<SortDirection>('asc');
  const [songSearchQuery, setSongSearchQuery] = useState('');

  // Fetch artist details
  const {
    data: artistData,
    error: artistError,
    networkStatus: artistNetworkStatus,
  } = useQuery(GetArtistDocument, {
    variables: { id: artistId },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  // Albums query variables
  const albumQueryVariables = useMemo(
    () => ({
      artistId: parseInt(artistId, 10),
      wanted:
        albumWantedFilter === 'all'
          ? undefined
          : albumWantedFilter === 'wanted',
      downloaded:
        albumDownloadFilter === 'all'
          ? undefined
          : albumDownloadFilter === 'downloaded',
      first: albumPageSize,
      sortBy: albumSortField,
      sortDirection: albumSortDirection,
      search: albumSearchQuery || undefined,
    }),
    [
      artistId,
      albumWantedFilter,
      albumDownloadFilter,
      albumPageSize,
      albumSortField,
      albumSortDirection,
      albumSearchQuery,
    ]
  );

  // Fetch albums for this artist
  const {
    data: albumsData,
    loading: albumsLoading,
    fetchMore: fetchMoreAlbums,
    networkStatus: albumsNetworkStatus,
  } = useQuery(GetAlbumsDocument, {
    variables: albumQueryVariables,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  // Songs query variables
  const songQueryVariables = useMemo(
    () => ({
      artistId: parseInt(artistId, 10),
      downloaded:
        songDownloadFilter === 'all'
          ? undefined
          : songDownloadFilter === 'downloaded',
      first: songPageSize,
      sortBy: songSortField,
      sortDirection: songSortDirection,
      search: songSearchQuery || undefined,
    }),
    [
      artistId,
      songDownloadFilter,
      songPageSize,
      songSortField,
      songSortDirection,
      songSearchQuery,
    ]
  );

  // Fetch songs for this artist
  const {
    data: songsData,
    loading: songsLoading,
    fetchMore: fetchMoreSongs,
    networkStatus: songsNetworkStatus,
  } = useQuery(GetSongsDocument, {
    variables: songQueryVariables,
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  // Mutations
  const [trackArtist] = useMutation(TrackArtistDocument);
  const [untrackArtist] = useMutation(UntrackArtistDocument);
  const [syncArtist] = useMutation(SyncArtistDocument);
  const [downloadArtist] = useMutation(DownloadArtistDocument);
  const [setAlbumWanted] = useMutation(SetAlbumWantedDocument);
  const [downloadAlbum] = useMutation(DownloadAlbumDocument);

  // Mutation state management
  const {
    mutatingIds: albumMutatingIds,
    pulseIds: albumPulseIds,
    handleMutation: handleAlbumMutation,
  } = useMutationState();
  const {
    loadingIds: syncMutatingIds,
    startLoading: startSync,
    stopLoading: stopSync,
  } = useMutationLoadingState();
  const {
    loadingIds: downloadMutatingIds,
    startLoading: startDownload,
    stopLoading: stopDownload,
  } = useMutationLoadingState();

  // Artist action handlers
  const handleTrackToggle = async () => {
    const artist = artistData?.artist;
    if (!artist) return;

    try {
      if (artist.isTracked) {
        await untrackArtist({ variables: { artistId: artist.id } });
        toast.success('Artist untracked');
      } else {
        await trackArtist({ variables: { artistId: artist.id } });
        toast.success('Artist tracked');
      }
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : 'Failed to update tracking'
      );
    }
  };

  const handleSyncArtist = async () => {
    const artist = artistData?.artist;
    if (!artist) return;

    try {
      startSync(artist.id);
      await syncArtist({ variables: { artistId: artist.id.toString() } });
      toast.success('Artist sync started');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Sync failed');
    } finally {
      stopSync(artist.id);
    }
  };

  const handleDownloadArtist = async () => {
    const artist = artistData?.artist;
    if (!artist) return;

    try {
      startDownload(artist.id);
      const result = await downloadArtist({
        variables: { artistId: artist.id.toString() },
      });
      if (result.data?.downloadArtist?.success) {
        toast.success('Artist download started');
      } else {
        toast.error(result.data?.downloadArtist?.message || 'Download failed');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Download failed');
    } finally {
      stopDownload(artist.id);
    }
  };

  // Album handlers
  const handleAlbumWantedFilterChange = (filter: WantedFilter) =>
    setAlbumWantedFilter(filter);
  const handleAlbumDownloadFilterChange = (filter: DownloadFilter) =>
    setAlbumDownloadFilter(filter);
  const handleAlbumPageSizeChange = (size: number) => setAlbumPageSize(size);
  const handleAlbumSearch = useCallback(
    (query: string) => setAlbumSearchQuery(query),
    []
  );

  const handleAlbumSort = (field: AlbumSortField) => {
    const newDirection: SortDirection =
      albumSortField === field && albumSortDirection === 'asc' ? 'desc' : 'asc';
    setAlbumSortField(field);
    setAlbumSortDirection(newDirection);
  };

  const handleAlbumWantedToggle = async (albumId: number, wanted: boolean) => {
    await handleAlbumMutation(
      albumId,
      async () => {
        await setAlbumWanted({ variables: { albumId, wanted } });
        toast.success(`Wanted ${wanted ? 'enabled' : 'disabled'}`);
      },
      { withPulse: true }
    );
  };

  const handleDownloadAlbum = async (albumId: number) => {
    await handleAlbumMutation(
      albumId,
      async () => {
        await downloadAlbum({ variables: { albumId: albumId.toString() } });
        toast.success('Album download queued');
      },
      { withPulse: false }
    );
  };

  const handleLoadMoreAlbums = () => {
    if (albumsData?.albums.pageInfo.hasNextPage) {
      fetchMoreAlbums({
        variables: {
          ...albumQueryVariables,
          after: albumsData.albums.pageInfo.endCursor,
        },
      });
    }
  };

  // Song handlers
  const handleSongDownloadFilterChange = (filter: DownloadFilter) =>
    setSongDownloadFilter(filter);
  const handleSongPageSizeChange = (size: number) => setSongPageSize(size);
  const handleSongSearch = useCallback(
    (query: string) => setSongSearchQuery(query),
    []
  );

  const handleSongSort = (field: SongSortField) => {
    const newDirection: SortDirection =
      songSortField === field && songSortDirection === 'asc' ? 'desc' : 'asc';
    setSongSortField(field);
    setSongSortDirection(newDirection);
  };

  const handleLoadMoreSongs = () => {
    if (songsData?.songs.pageInfo.hasNextPage) {
      fetchMoreSongs({
        variables: {
          ...songQueryVariables,
          after: songsData.songs.pageInfo.endCursor,
        },
      });
    }
  };

  // Derived state
  const artist = artistData?.artist;
  const albums = (albumsData?.albums.edges as Album[]) || [];
  const albumsTotalCount = albumsData?.albums.totalCount || 0;
  const albumsPageInfo = albumsData?.albums.pageInfo;

  const songs = (songsData?.songs.edges as Song[]) || [];
  const songsTotalCount = songsData?.songs.totalCount || 0;
  const songsPageInfo = songsData?.songs.pageInfo;

  const { isRefreshing: artistRefreshing, isInitial: artistInitialLoading } =
    useRequestState(artistNetworkStatus);
  const { isRefreshing: albumsRefreshing } =
    useRequestState(albumsNetworkStatus);
  const { isRefreshing: songsRefreshing } = useRequestState(songsNetworkStatus);

  return {
    // Artist data
    artist,
    artistError,
    artistRefreshing,
    artistInitialLoading,

    // Artist actions
    handleTrackToggle,
    handleSyncArtist,
    handleDownloadArtist,
    syncMutatingIds,
    downloadMutatingIds,

    // Albums data
    albums,
    albumsTotalCount,
    albumsPageInfo,
    albumsLoading,
    albumsRefreshing,

    // Albums filters & sorting
    albumWantedFilter,
    albumDownloadFilter,
    albumPageSize,
    albumSortField,
    albumSortDirection,

    // Albums mutation states
    albumMutatingIds,
    albumPulseIds,

    // Albums handlers
    handleAlbumWantedFilterChange,
    handleAlbumDownloadFilterChange,
    handleAlbumPageSizeChange,
    handleAlbumSort,
    handleAlbumSearch,
    handleAlbumWantedToggle,
    handleDownloadAlbum,
    handleLoadMoreAlbums,

    // Songs data
    songs,
    songsTotalCount,
    songsPageInfo,
    songsLoading,
    songsRefreshing,

    // Songs filters & sorting
    songDownloadFilter,
    songPageSize,
    songSortField,
    songSortDirection,

    // Songs handlers
    handleSongDownloadFilterChange,
    handleSongPageSizeChange,
    handleSongSort,
    handleSongSearch,
    handleLoadMoreSongs,
  };
}
