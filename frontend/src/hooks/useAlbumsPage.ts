import { useState, useMemo, useCallback } from 'react';
import { useMutation, useQuery } from '@apollo/client/react';
import {
  GetAlbumsDocument,
  SetAlbumWantedDocument,
  DownloadAlbumDocument,
  GetArtistDocument,
  type Album,
  type GetAlbumsQuery,
} from '../types/generated/graphql';
import { useToast } from '../components/ui/useToast';
import { useMutationState } from './useMutationState';
import { useRequestState } from './useRequestState';
import {
  usePrefetchFilters,
  generateFilterCombinations,
} from './usePrefetchFilters';
import { useQueryPrefetch } from './useQueryPrefetch';
import type { AlbumSortField } from '../components/albums/AlbumsTable';
import type {
  SortDirection,
  WantedFilter,
  DownloadFilter,
} from '../types/shared';

interface UseAlbumsPageOptions {
  artistId?: number;
}

export function useAlbumsPage(options: UseAlbumsPageOptions = {}) {
  const toast = useToast();
  const { artistId } = options;

  // State
  const [wantedFilter, setWantedFilter] = useState<WantedFilter>('all');
  const [downloadFilter, setDownloadFilter] = useState<DownloadFilter>('all');
  const [pageSize, setPageSize] = useState(50);
  const [sortField, setSortField] = useState<AlbumSortField>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [searchQuery, setSearchQuery] = useState('');

  // Memoize query variables
  const queryVariables = useMemo(
    () => ({
      artistId: artistId || undefined,
      wanted: wantedFilter === 'all' ? undefined : wantedFilter === 'wanted',
      downloaded:
        downloadFilter === 'all' ? undefined : downloadFilter === 'downloaded',
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [
      artistId,
      wantedFilter,
      downloadFilter,
      pageSize,
      sortField,
      sortDirection,
      searchQuery,
    ]
  );

  // Data fetching
  const { data, loading, error, fetchMore, networkStatus } = useQuery(
    GetAlbumsDocument,
    {
      variables: queryVariables,
      fetchPolicy: 'cache-and-network',
      notifyOnNetworkStatusChange: true,
      pollInterval: 0,
      errorPolicy: 'all',
    }
  );

  // Fetch artist details if filtering by artist
  const { data: artistData } = useQuery(GetArtistDocument, {
    variables: { id: artistId?.toString() ?? '0' },
    skip: !artistId,
    fetchPolicy: 'cache-first',
    nextFetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: false,
    pollInterval: 0,
  });

  // Mutations
  const [setAlbumWanted] = useMutation(SetAlbumWantedDocument);
  const [downloadAlbum] = useMutation(DownloadAlbumDocument);
  const { mutatingIds, pulseIds, handleMutation } = useMutationState();

  // Prefetching setup
  const createPrefetchHandler = useQueryPrefetch(
    GetAlbumsDocument,
    queryVariables
  );

  const baseVariables = useMemo(
    () => ({
      artistId: artistId || undefined,
      first: pageSize,
      sortBy: sortField,
      sortDirection: sortDirection,
      search: searchQuery || undefined,
    }),
    [artistId, pageSize, sortField, sortDirection, searchQuery]
  );

  const filterCombinations = useMemo(
    () =>
      generateFilterCombinations({
        wanted: [true, false],
        downloaded: [true, false],
      }),
    []
  );

  usePrefetchFilters({
    query: GetAlbumsDocument,
    baseVariables,
    filterCombinations,
    enabled: !!data,
    networkStatus,
  });

  // Handlers
  const handleWantedFilterChange = createPrefetchHandler(
    setWantedFilter,
    (newFilter: WantedFilter) => ({
      wanted: newFilter === 'all' ? undefined : newFilter === 'wanted',
    })
  );

  const handleDownloadFilterChange = createPrefetchHandler(
    setDownloadFilter,
    (newFilter: DownloadFilter) => ({
      downloaded: newFilter === 'all' ? undefined : newFilter === 'downloaded',
    })
  );

  const handlePageSizeChange = createPrefetchHandler(setPageSize, newSize => ({
    first: newSize,
  }));

  const handleSort = (field: AlbumSortField) => {
    const newDirection: SortDirection =
      sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';

    setSortField(field);
    setSortDirection(newDirection);

    createPrefetchHandler(null, () => ({
      sortBy: field,
      sortDirection: newDirection,
    }))(field);
  };

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleWantedToggle = async (albumId: number, wanted: boolean) => {
    await handleMutation(
      albumId,
      async () => {
        await setAlbumWanted({
          variables: {
            albumId,
            wanted,
          },
        });
        toast.success(`Wanted ${wanted ? 'enabled' : 'disabled'}`);
      },
      { withPulse: true }
    );
  };

  const handleDownloadAlbum = async (albumId: number) => {
    await handleMutation(
      albumId,
      async () => {
        await downloadAlbum({
          variables: {
            albumId: albumId.toString(),
          },
        });
        toast.success('Album download queued');
      },
      { withPulse: false }
    );
  };

  const handleLoadMore = () => {
    if (data?.albums.pageInfo.hasNextPage) {
      fetchMore({
        variables: {
          after: data.albums.pageInfo.endCursor,
        },
        updateQuery: (
          prevResult: GetAlbumsQuery,
          { fetchMoreResult }: { fetchMoreResult?: GetAlbumsQuery }
        ) => {
          if (!fetchMoreResult) return prevResult;

          return {
            albums: {
              ...fetchMoreResult.albums,
              edges: [
                ...prevResult.albums.edges,
                ...fetchMoreResult.albums.edges,
              ],
            },
          };
        },
      });
    }
  };

  // Derived state
  const albums = (data?.albums.edges as Album[]) || [];
  const totalCount = data?.albums.totalCount || 0;
  const pageInfo = data?.albums.pageInfo;
  const { isRefreshing, isInitial: isInitialLoading } =
    useRequestState(networkStatus);

  const artist = artistData?.artist;

  return {
    // Data
    albums,
    totalCount,
    pageInfo,
    loading,
    error,
    isRefreshing,
    isInitialLoading,
    artist,

    // Filters & sorting
    wantedFilter,
    downloadFilter,
    pageSize,
    sortField,
    sortDirection,
    searchQuery,

    // Mutation states
    mutatingIds,
    pulseIds,

    // Handlers
    handleWantedFilterChange,
    handleDownloadFilterChange,
    handlePageSizeChange,
    handleSort,
    handleSearch,
    handleWantedToggle,
    handleDownloadAlbum,
    handleLoadMore,
  };
}
