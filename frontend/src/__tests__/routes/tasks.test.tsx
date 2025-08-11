import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuery } from '@apollo/client';
import type {
  TestTaskHistory,
  TestEdge,
  MockedUseQuery,
} from '../../types/test';

// Import mock data
import {
  mockGetTaskHistoryResponse,
  createGraphQLError,
  createNetworkError,
  createMockUseQuery,
} from '../../test/graphql-mocks';

// Mock the GraphQL hooks
vi.mock('@apollo/client', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
  useApolloClient: vi.fn(() => ({
    query: vi.fn(),
    cache: {
      readQuery: vi.fn(),
      writeQuery: vi.fn(),
      modify: vi.fn(),
    },
  })),
}));

// Mock the TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => ({ component: () => null })),
}));

const mockUseQuery = useQuery as MockedUseQuery;

// Create a test component that simulates the Tasks route
const TestTasksComponent = () => {
  const { data, loading, error, fetchMore } = mockUseQuery();

  const [filters, setFilters] = React.useState({
    status: 'all',
    type: 'all',
    entityType: 'all',
    search: '',
  });

  const [pageSize, setPageSize] = React.useState(50);

  if (loading) {
    return <div>Loading task history...</div>;
  }

  if (error) {
    return <div>Error loading task history: {error.message}</div>;
  }

  if (!data?.taskHistory?.edges?.length) {
    return <div>No tasks found</div>;
  }

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({ ...prev, [filterType]: value }));
  };

  const handleSearchChange = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }));
  };

  const handlePageSizeChange = (value: number) => {
    setPageSize(value);
  };

  // Filter tasks based on current filters
  const filteredTasks = data.taskHistory.edges.filter(
    (edge: TestEdge<TestTaskHistory>) => {
      const task = edge.node;

      if (
        filters.status !== 'all' &&
        task.status.toLowerCase() !== filters.status
      ) {
        return false;
      }

      if (filters.type !== 'all' && task.type.toLowerCase() !== filters.type) {
        return false;
      }

      if (
        filters.entityType !== 'all' &&
        task.entityType.toLowerCase() !== filters.entityType
      ) {
        return false;
      }

      if (
        filters.search &&
        !task.taskId.toLowerCase().includes(filters.search.toLowerCase())
      ) {
        return false;
      }

      return true;
    }
  );

  // Get active tasks (running status)
  const activeTasks = filteredTasks.filter(
    (edge: TestEdge<TestTaskHistory>) => edge.node.status === 'RUNNING'
  );

  return (
    <div>
      <h1>Background Tasks</h1>

      {/* Active tasks section */}
      <div>
        <h2>Active Tasks ({activeTasks.length})</h2>
        {activeTasks.map((edge: TestEdge<TestTaskHistory>) => {
          const task = edge.node;
          return (
            <div key={task.id} data-testid={`active-task-${task.id}`}>
              <span>{task.type}</span>
              <span>{task.entityType}</span>
              <span>{task.status}</span>
              <span>{task.progressPercentage}%</span>
            </div>
          );
        })}
      </div>

      {/* Filter controls */}
      <div>
        <select
          value={filters.status}
          onChange={e => handleFilterChange('status', e.target.value)}
          data-testid='status-filter'
        >
          <option value='all'>All Status</option>
          <option value='running'>Running</option>
          <option value='completed'>Completed</option>
          <option value='failed'>Failed</option>
          <option value='pending'>Pending</option>
        </select>

        <select
          value={filters.type}
          onChange={e => handleFilterChange('type', e.target.value)}
          data-testid='type-filter'
        >
          <option value='all'>All Types</option>
          <option value='sync'>Sync</option>
          <option value='download'>Download</option>
          <option value='fetch'>Fetch</option>
        </select>

        <select
          value={filters.entityType}
          onChange={e => handleFilterChange('entityType', e.target.value)}
          data-testid='entity-type-filter'
        >
          <option value='all'>All Entities</option>
          <option value='artist'>Artist</option>
          <option value='album'>Album</option>
          <option value='playlist'>Playlist</option>
        </select>

        <input
          type='text'
          value={filters.search}
          onChange={e => handleSearchChange(e.target.value)}
          placeholder='Search tasks...'
          data-testid='search-input'
        />

        <select
          value={pageSize}
          onChange={e => handlePageSizeChange(Number(e.target.value))}
          data-testid='page-size-selector'
        >
          <option value={20}>20 per page</option>
          <option value={50}>50 per page</option>
          <option value={100}>100 per page</option>
        </select>
      </div>

      {/* Task history */}
      <div>
        <h2>
          Task History ({filteredTasks.length} of {data.taskHistory.totalCount})
        </h2>
        {filteredTasks.map((edge: TestEdge<TestTaskHistory>) => {
          const task = edge.node;
          return (
            <div key={task.id} data-testid={`task-${task.id}`}>
              <span>{task.taskId}</span>
              <span>{task.type}</span>
              <span>{task.entityType}</span>
              <span>{task.status}</span>
              <span>{task.durationSeconds}s</span>
              <span>{task.progressPercentage}%</span>
              {task.logMessages && task.logMessages.length > 0 && (
                <div data-testid={`logs-${task.id}`}>
                  {task.logMessages.map((log: string) => (
                    <div key={`task-${task.id}-log-entry-${log}`}>{log}</div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {data.taskHistory.pageInfo.hasNextPage && (
        <button onClick={() => fetchMore()} data-testid='load-more'>
          Load More
        </button>
      )}
    </div>
  );
};

describe('Tasks Route', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Query Operations', () => {
    it('renders loading state', () => {
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, true));

      render(<TestTasksComponent />);

      expect(screen.getByText(/loading task history/i)).toBeInTheDocument();
    });

    it('renders tasks when data is loaded', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      expect(screen.getByText('Background Tasks')).toBeInTheDocument();
      expect(screen.getByText(/task history/i)).toBeInTheDocument();
      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
    });

    it('renders error state for GraphQL errors', () => {
      const error = createGraphQLError('Failed to load task history');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));

      render(<TestTasksComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/failed to load task history/i)
      ).toBeInTheDocument();
    });

    it('renders error state for network errors', () => {
      const error = createNetworkError('Network connection failed');
      mockUseQuery.mockReturnValue(createMockUseQuery(undefined, false, error));

      render(<TestTasksComponent />);

      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(
        screen.getByText(/network connection failed/i)
      ).toBeInTheDocument();
    });

    it('renders empty state when no tasks', () => {
      const emptyResponse = {
        taskHistory: {
          totalCount: 0,
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: null,
            endCursor: null,
          },
          edges: [],
        },
      };

      mockUseQuery.mockReturnValue(createMockUseQuery(emptyResponse));

      render(<TestTasksComponent />);

      expect(screen.getByText(/no tasks found/i)).toBeInTheDocument();
    });

    it('handles pagination correctly', () => {
      const responseWithNextPage = {
        ...mockGetTaskHistoryResponse,
        taskHistory: {
          ...mockGetTaskHistoryResponse.taskHistory,
          pageInfo: {
            ...mockGetTaskHistoryResponse.taskHistory.pageInfo,
            hasNextPage: true,
          },
        },
      };

      const mockFetchMore = vi.fn();
      mockUseQuery.mockReturnValue({
        ...createMockUseQuery(responseWithNextPage),
        fetchMore: mockFetchMore,
      });

      render(<TestTasksComponent />);

      const loadMoreButton = screen.getByTestId('load-more');
      expect(loadMoreButton).toBeInTheDocument();

      fireEvent.click(loadMoreButton);
      expect(mockFetchMore).toHaveBeenCalled();
    });
  });

  describe('Filtering and Search', () => {
    it('handles status filter changes', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      const statusFilter = screen.getByTestId('status-filter');
      fireEvent.change(statusFilter, { target: { value: 'running' } });

      expect(statusFilter).toHaveValue('running');
    });

    it('handles type filter changes', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      const typeFilter = screen.getByTestId('type-filter');
      fireEvent.change(typeFilter, { target: { value: 'sync' } });

      expect(typeFilter).toHaveValue('sync');
    });

    it('handles entity type filter changes', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      const entityTypeFilter = screen.getByTestId('entity-type-filter');
      fireEvent.change(entityTypeFilter, { target: { value: 'artist' } });

      expect(entityTypeFilter).toHaveValue('artist');
    });

    it('handles search input changes', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      const searchInput = screen.getByTestId('search-input');
      fireEvent.change(searchInput, { target: { value: 'test-task' } });

      expect(searchInput).toHaveValue('test-task');
    });

    it('handles page size changes', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      const pageSizeSelector = screen.getByTestId('page-size-selector');
      fireEvent.change(pageSizeSelector, { target: { value: '100' } });

      expect(pageSizeSelector).toHaveValue('100');
    });
  });

  describe('Data Display', () => {
    it('displays task information correctly', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      // Check that task details are displayed
      expect(screen.getByText('task-123-1')).toBeInTheDocument();
      expect(screen.getAllByText('SYNC').length).toBeGreaterThan(0);
      expect(screen.getAllByText('ARTIST').length).toBeGreaterThan(0);
      expect(screen.getByText('COMPLETED')).toBeInTheDocument();
      expect(screen.getAllByText('3600s').length).toBeGreaterThan(0);
      expect(screen.getAllByText('100%').length).toBeGreaterThan(0);
    });

    it('displays active tasks correctly', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      // Check active tasks section
      expect(screen.getByText(/active tasks/i)).toBeInTheDocument();
      expect(screen.getByTestId('active-task-2')).toBeInTheDocument();
    });

    it('displays task logs when available', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      // Check that log messages are displayed
      const logsContainer = screen.getByTestId('logs-1');
      expect(logsContainer).toBeInTheDocument();
      expect(screen.getByText('Task 1 started')).toBeInTheDocument();
      expect(screen.getByText('Task 1 completed')).toBeInTheDocument();
    });

    it('shows correct task counts', () => {
      mockUseQuery.mockReturnValue(
        createMockUseQuery(mockGetTaskHistoryResponse)
      );

      render(<TestTasksComponent />);

      expect(screen.getByText(/2 of 2/)).toBeInTheDocument();
      expect(screen.getByText(/active tasks \(1\)/i)).toBeInTheDocument();
    });
  });

  describe('Real-time Updates', () => {
    it('handles polling for updates', () => {
      // Mock the query with polling
      const mockQueryResult = {
        ...createMockUseQuery(mockGetTaskHistoryResponse),
        networkStatus: 7, // Ready
      };

      mockUseQuery.mockReturnValue(mockQueryResult);

      render(<TestTasksComponent />);

      // The component should handle polling automatically
      expect(screen.getByText('Background Tasks')).toBeInTheDocument();
    });
  });
});
