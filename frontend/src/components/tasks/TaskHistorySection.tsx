import { useState, useEffect } from 'react';
import type { TaskHistoryEdge } from '../../types/generated/graphql';
import type { TaskStatus, TaskType, EntityType } from '../../types/shared';
import { SearchInput } from '../ui/SearchInput';
import { PageSizeSelector } from '../ui/PageSizeSelector';
import { LoadMoreButton } from '../ui/LoadMoreButton';
import EnhancedEntityDisplay from '../EnhancedEntityDisplay';

interface TaskHistoryPageInfo {
  hasNextPage: boolean;
  endCursor: string | null;
}

interface TaskHistoryData {
  taskHistory: {
    edges: TaskHistoryEdge[];
    totalCount: number;
    pageInfo: TaskHistoryPageInfo;
  };
}

interface TaskHistorySectionProps {
  // Data
  data: TaskHistoryData | undefined;
  loading: boolean;
  error: Error | undefined;
  isRefreshing: boolean;
  lastUpdated: Date;

  // Filters
  statusFilter: TaskStatus;
  typeFilter: TaskType;
  entityFilter: EntityType;
  searchQuery: string;
  pageSize: number;

  // Filter handlers
  onStatusFilterChange: (status: TaskStatus) => void;
  onTypeFilterChange: (type: TaskType) => void;
  onEntityFilterChange: (entity: EntityType) => void;
  onSearchChange: (query: string) => void;
  onPageSizeChange: (size: number) => void;

  // Actions
  onLoadMore: () => void;
}

function useRelativeTime(date: Date): string {
  const [relativeTime, setRelativeTime] = useState('');

  useEffect(() => {
    const updateRelativeTime = () => {
      const now = new Date();
      const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000);

      if (secondsAgo < 10) {
        setRelativeTime('just now');
      } else if (secondsAgo < 45) {
        setRelativeTime('30 seconds ago');
      } else if (secondsAgo < 90) {
        setRelativeTime('a minute ago');
      } else if (secondsAgo < 300) {
        setRelativeTime('a few minutes ago');
      } else if (secondsAgo < 600) {
        setRelativeTime('5 minutes ago');
      } else if (secondsAgo < 1800) {
        setRelativeTime('10 minutes ago');
      } else if (secondsAgo < 3600) {
        setRelativeTime('30 minutes ago');
      } else if (secondsAgo < 7200) {
        setRelativeTime('an hour ago');
      } else {
        const hours = Math.floor(secondsAgo / 3600);
        setRelativeTime(`${hours} hours ago`);
      }
    };

    updateRelativeTime();
    // Update every 5 seconds instead of every second
    const interval = setInterval(updateRelativeTime, 5000);

    return () => clearInterval(interval);
  }, [date]);

  return relativeTime;
}

export function TaskHistorySection({
  data,
  loading,
  error,
  isRefreshing,
  lastUpdated,
  statusFilter,
  typeFilter,
  entityFilter,
  searchQuery,
  pageSize,
  onStatusFilterChange,
  onTypeFilterChange,
  onEntityFilterChange,
  onSearchChange,
  onPageSizeChange,
  onLoadMore,
}: TaskHistorySectionProps) {
  const [expandedLogs, setExpandedLogs] = useState<Record<string, boolean>>({});
  const relativeTime = useRelativeTime(lastUpdated);

  return (
    <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
      <div className='px-6 py-4 border-b border-gray-200'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-3'>
            <h2 className='text-lg font-semibold text-gray-900'>
              Task History
            </h2>
            <div className='flex items-center gap-1.5 text-xs text-gray-500'>
              {isRefreshing ? (
                <>
                  <div className='animate-spin rounded-full h-3 w-3 border-2 border-blue-500 border-t-transparent' />
                  <span className='text-blue-600'>Updating...</span>
                </>
              ) : (
                <>
                  <svg
                    className='h-3 w-3 text-green-500'
                    fill='currentColor'
                    viewBox='0 0 20 20'
                  >
                    <path
                      fillRule='evenodd'
                      d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
                      clipRule='evenodd'
                    />
                  </svg>
                  <span
                    title={lastUpdated.toLocaleString()}
                    className='cursor-help'
                  >
                    Updated {relativeTime}
                  </span>
                </>
              )}
            </div>
          </div>
          <div className='flex items-center gap-4'>
            <SearchInput
              onSearch={onSearchChange}
              initialValue={searchQuery}
              placeholder='Search tasks...'
              className='w-64'
            />
            <select
              value={statusFilter}
              onChange={e => onStatusFilterChange(e.target.value as TaskStatus)}
              className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            >
              <option value='all'>All Status</option>
              <option value='running'>Running</option>
              <option value='completed'>Completed</option>
              <option value='failed'>Failed</option>
              <option value='pending'>Pending</option>
            </select>
            <select
              value={typeFilter}
              onChange={e => onTypeFilterChange(e.target.value as TaskType)}
              className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            >
              <option value='all'>All Types</option>
              <option value='sync'>Sync</option>
              <option value='download'>Download</option>
              <option value='fetch'>Fetch</option>
            </select>
            <select
              value={entityFilter}
              onChange={e => onEntityFilterChange(e.target.value as EntityType)}
              className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
            >
              <option value='all'>All Entities</option>
              <option value='artist'>Artist</option>
              <option value='album'>Album</option>
              <option value='playlist'>Playlist</option>
            </select>
            <PageSizeSelector
              pageSize={pageSize}
              onPageSizeChange={onPageSizeChange}
              options={[20, 50, 100]}
            />
          </div>
        </div>
      </div>

      <div className='p-6'>
        {loading && !isRefreshing && !data ? (
          <div className='text-center py-8'>
            <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto' />
            <p className='mt-2 text-gray-600'>Loading task history...</p>
          </div>
        ) : error ? (
          <div className='text-center py-8 text-red-600'>
            <p>Error loading task history: {error.message}</p>
          </div>
        ) : data?.taskHistory?.edges?.length === 0 ? (
          <div className='text-center py-8 text-gray-500'>
            <div className='text-4xl mb-4'>📝</div>
            <p>No task history found</p>
            <p className='text-sm'>
              Task history will appear here as tasks are executed
            </p>
          </div>
        ) : (
          <div className='space-y-3'>
            <div className='overflow-x-auto'>
              <table className='min-w-full divide-y divide-gray-200 text-sm'>
                <thead className='bg-gray-50'>
                  <tr>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Status
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Type
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700 w-48'>
                      Entity
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Task ID
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Started
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Completed
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Duration
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Progress
                    </th>
                    <th className='px-3 py-2 text-left font-medium text-gray-700'>
                      Logs
                    </th>
                  </tr>
                </thead>
                <tbody className='divide-y divide-gray-100'>
                  {data?.taskHistory?.edges?.map((edge: TaskHistoryEdge) => {
                    const task = edge.node;
                    const isLogsOpen = !!expandedLogs[task.id];
                    return (
                      <>
                        <tr key={task.id} className='hover:bg-gray-50'>
                          <td className='px-3 py-2 whitespace-nowrap'>
                            <span
                              className={`inline-block w-2.5 h-2.5 rounded-full align-middle ${
                                task.status === 'RUNNING'
                                  ? 'bg-blue-500'
                                  : task.status === 'COMPLETED'
                                    ? 'bg-green-500'
                                    : task.status === 'FAILED'
                                      ? 'bg-red-500'
                                      : 'bg-gray-400'
                              }`}
                              title={task.status}
                            />
                            <span className='ml-2 text-gray-700 text-xs sm:text-sm'>
                              {task.status}
                            </span>
                          </td>
                          <td className='px-3 py-2 whitespace-nowrap text-gray-900'>
                            {task.type.charAt(0).toUpperCase() +
                              task.type.slice(1)}
                          </td>
                          <td className='px-3 py-2 text-gray-700 max-w-xs'>
                            <EnhancedEntityDisplay
                              entityType={task.entityType}
                              entityId={task.entityId}
                              compact={true}
                            />
                          </td>
                          <td className='px-3 py-2 whitespace-nowrap text-gray-700'>
                            <span className='font-mono text-xs'>
                              {task.taskId}
                            </span>
                          </td>
                          <td
                            className='px-3 py-2 whitespace-nowrap text-gray-700'
                            title={new Date(task.startedAt).toLocaleString()}
                          >
                            {new Date(task.startedAt).toLocaleTimeString()}
                          </td>
                          <td
                            className='px-3 py-2 whitespace-nowrap text-gray-700'
                            title={
                              task.completedAt
                                ? new Date(task.completedAt).toLocaleString()
                                : undefined
                            }
                          >
                            {task.completedAt
                              ? new Date(task.completedAt).toLocaleTimeString()
                              : '-'}
                          </td>
                          <td className='px-3 py-2 whitespace-nowrap text-gray-700'>
                            {task.durationSeconds
                              ? `${task.durationSeconds}s`
                              : '-'}
                          </td>
                          <td className='px-3 py-2 whitespace-nowrap text-gray-700'>
                            {task.progressPercentage !== null &&
                            task.progressPercentage !== undefined
                              ? `${task.progressPercentage}%`
                              : '-'}
                          </td>
                          <td className='px-3 py-2 whitespace-nowrap'>
                            {task.logMessages && task.logMessages.length > 0 ? (
                              <button
                                type='button'
                                className='text-indigo-600 hover:underline text-sm'
                                onClick={() =>
                                  setExpandedLogs(prev => ({
                                    ...prev,
                                    [task.id]: !isLogsOpen,
                                  }))
                                }
                                aria-expanded={isLogsOpen}
                              >
                                {isLogsOpen
                                  ? 'Hide logs'
                                  : `Show logs (${task.logMessages.length})`}
                              </button>
                            ) : (
                              <span className='text-gray-400 text-sm'>
                                None
                              </span>
                            )}
                          </td>
                        </tr>
                        {isLogsOpen && task.logMessages && (
                          <tr>
                            <td colSpan={9} className='px-3 pb-3'>
                              <div className='mt-1 bg-gray-50 rounded p-3 text-xs sm:text-sm font-mono text-gray-700 max-h-40 overflow-y-auto'>
                                {task.logMessages.map(
                                  (log: string, idx: number) => (
                                    <div
                                      // eslint-disable-next-line react/no-array-index-key
                                      key={`task-${task.id}-log-${idx}`}
                                      className='mb-1'
                                    >
                                      {log}
                                    </div>
                                  )
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {data?.taskHistory?.pageInfo?.hasNextPage && (
              <LoadMoreButton
                hasNextPage={data.taskHistory.pageInfo.hasNextPage}
                loading={loading}
                remainingCount={
                  data.taskHistory.totalCount - data.taskHistory.edges.length
                }
                onLoadMore={onLoadMore}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
