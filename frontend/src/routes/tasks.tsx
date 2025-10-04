import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client/react';
import { useState, useCallback, useMemo } from 'react';
import { SearchInput } from '../components/ui/SearchInput';
import { useRequestState } from '../hooks/useRequestState';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import {
  GetTaskHistoryDocument,
  GetQueueStatusDocument,
  CancelTasksByNameDocument,
  CancelRunningTasksByNameDocument,
  CancelAllTasksDocument,
  type TaskHistory,
  type TaskHistoryEdge,
} from '../types/generated/graphql';
import EnhancedEntityDisplay from '../components/EnhancedEntityDisplay';
import { useToast } from '../components/ui/useToast';
import { useConfirm } from '../hooks/useConfirm';
import { TaskStatsHeader } from '../components/tasks/TaskStatsHeader';
import { QueueManagementSection } from '../components/tasks/QueueManagementSection';
import { ActiveTasksSection } from '../components/tasks/ActiveTasksSection';
import type { TaskStatus, TaskType, EntityType } from '../types/shared';

function Tasks() {
  const [activeTasksFilter, setActiveTasksFilter] = useState<TaskType>('all');
  const [activeTasksEntityFilter, setActiveTasksEntityFilter] =
    useState<EntityType>('all');

  const [historyFilter, setHistoryFilter] = useState<TaskStatus>('all');
  const [historyTypeFilter, setHistoryTypeFilter] = useState<TaskType>('all');
  const [historyEntityFilter, setHistoryEntityFilter] =
    useState<EntityType>('all');
  const [pageSize, setPageSize] = useState(50);
  const [searchQuery, setSearchQuery] = useState('');

  const [expandedLogs, setExpandedLogs] = useState<Record<string, boolean>>({});
  const [expandedHistoryLogs, setExpandedHistoryLogs] = useState<
    Record<string, boolean>
  >({});

  const toast = useToast();
  const { confirm, ConfirmDialog } = useConfirm();

  const [cancelTasksByName] = useMutation(CancelTasksByNameDocument);
  const [cancelRunningTasksByName] = useMutation(
    CancelRunningTasksByNameDocument
  );
  const [cancelAllTasksEnhanced] = useMutation(CancelAllTasksDocument);

  const {
    data: historyData,
    loading: historyLoading,
    error: historyError,
    fetchMore,
    networkStatus: historyNetworkStatus,
  } = useQuery(GetTaskHistoryDocument, {
    variables: {
      status: historyFilter === 'all' ? undefined : historyFilter,
      type: historyTypeFilter === 'all' ? undefined : historyTypeFilter,
      entityType:
        historyEntityFilter === 'all' ? undefined : historyEntityFilter,
      search: searchQuery || undefined,
      first: pageSize,
    },
    fetchPolicy: 'cache-first',
    notifyOnNetworkStatusChange: true,
    pollInterval: 8000,
  });

  const {
    data: queueData,
    loading: queueLoading,
    refetch: refetchQueue,
  } = useQuery(GetQueueStatusDocument, {
    pollInterval: 5000,
  });

  const { isRefreshing: isHistoryRefreshing } =
    useRequestState(historyNetworkStatus);

  const historyNodes = useMemo<TaskHistory[]>(
    () => historyData?.taskHistory?.edges?.map(edge => edge.node) || [],
    [historyData?.taskHistory?.edges]
  );

  // Single-pass filtering and categorization for better performance
  const taskCategories = useMemo(() => {
    const categories = {
      running: [] as TaskHistory[],
      completed: [] as TaskHistory[],
      failed: [] as TaskHistory[],
      allActive: [] as TaskHistory[],
    };

    for (const task of historyNodes) {
      // Only process RUNNING tasks for active tasks section
      if (task.status === 'RUNNING') {
        categories.allActive.push(task);

        // Apply type/entity filters
        const matchesTypeFilter =
          activeTasksFilter === 'all' ||
          task.type.toLowerCase() === activeTasksFilter;
        const matchesEntityFilter =
          activeTasksEntityFilter === 'all' ||
          task.entityType.toLowerCase() === activeTasksEntityFilter;

        if (matchesTypeFilter && matchesEntityFilter) {
          categories.running.push(task);
        }
      }
    }

    return categories;
  }, [historyNodes, activeTasksFilter, activeTasksEntityFilter]);

  const { running: runningTasks } = taskCategories;
  // Note: completedTasks and failedTasks were only used in filteredActiveTasks which was incorrect
  // (they filtered from realActiveTasks which were all RUNNING, so completed/failed would always be empty)
  const completedTasks: TaskHistory[] = [];
  const failedTasks: TaskHistory[] = [];

  // Memoize stats calculations for the stats cards
  const taskStats = useMemo(() => {
    const today = new Date().toDateString();
    let completedToday = 0;
    let failedToday = 0;
    let totalCompleted = 0;
    let totalFailed = 0;

    for (const task of historyNodes) {
      if (task.status === 'COMPLETED') {
        totalCompleted++;
        if (
          task.completedAt &&
          new Date(task.completedAt).toDateString() === today
        ) {
          completedToday++;
        }
      } else if (task.status === 'FAILED') {
        totalFailed++;
        if (
          task.completedAt &&
          new Date(task.completedAt).toDateString() === today
        ) {
          failedToday++;
        }
      }
    }

    const total = totalCompleted + totalFailed;
    const successRate =
      total > 0 ? Math.round((totalCompleted / total) * 100) : 0;

    return {
      completedToday,
      failedToday,
      successRate,
    };
  }, [historyNodes]);

  // Reusable handler for task cancellation with confirmation
  const handleCancelWithConfirmation = useCallback(
    async <T extends Record<string, unknown>>(
      confirmMessage: string,
      mutationFn: () => Promise<{ data?: T | null }>,
      successMessage: string,
      errorPrefix: string = 'Failed to cancel tasks'
    ) => {
      const confirmed = await confirm({
        title: 'Confirm Cancellation',
        message: confirmMessage,
        confirmText: 'Cancel Tasks',
        cancelText: 'Keep Tasks',
        variant: 'danger',
      });

      if (!confirmed) return;

      try {
        const result = await mutationFn();
        if (!result.data) {
          toast.error(`${errorPrefix}: No data returned`);
          return;
        }

        const firstKey = Object.keys(result.data)[0];
        const data = result.data[firstKey] as
          | { success?: boolean; message?: string }
          | undefined;

        if (data?.success) {
          toast.success(successMessage);
          refetchQueue();
        } else {
          toast.error(`${errorPrefix}: ${data?.message || 'Unknown error'}`);
        }
      } catch (error) {
        toast.error(
          `Error cancelling tasks: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    },
    [confirm, toast, refetchQueue]
  );

  const handleCancelAllTasks = useCallback(
    () =>
      handleCancelWithConfirmation(
        'Are you sure you want to cancel all tasks (both pending and running)? This action cannot be undone.',
        () => cancelAllTasksEnhanced(),
        'Successfully cancelled all tasks'
      ),
    [handleCancelWithConfirmation, cancelAllTasksEnhanced]
  );

  const handleCancelTasksByName = useCallback(
    (taskName: string) =>
      handleCancelWithConfirmation(
        `Are you sure you want to cancel all '${taskName}' tasks? This action cannot be undone.`,
        () => cancelTasksByName({ variables: { taskName } }),
        `Successfully cancelled ${taskName} tasks`
      ),
    [handleCancelWithConfirmation, cancelTasksByName]
  );

  const handleCancelRunningTasksByName = useCallback(
    (taskName: string) =>
      handleCancelWithConfirmation(
        `Are you sure you want to cancel all running '${taskName}' tasks? This action cannot be undone.`,
        () => cancelRunningTasksByName({ variables: { taskName } }),
        `Successfully cancelled running ${taskName} tasks`,
        'Failed to cancel running tasks'
      ),
    [handleCancelWithConfirmation, cancelRunningTasksByName]
  );

  const handleRefresh = useCallback(() => {
    window.location.reload();
  }, []);

  return (
    <div className='space-y-8'>
      <TaskStatsHeader
        runningTasksCount={runningTasks.length}
        completedTodayCount={taskStats.completedToday}
        failedTodayCount={taskStats.failedToday}
        successRate={taskStats.successRate}
        queueLoading={queueLoading}
        onRefresh={handleRefresh}
      />

      <QueueManagementSection
        queueLoading={queueLoading}
        totalPendingTasks={queueData?.queueStatus?.totalPendingTasks || 0}
        taskCounts={queueData?.queueStatus?.taskCounts || []}
        onCancelTasksByName={handleCancelTasksByName}
        onCancelAllTasks={handleCancelAllTasks}
      />

      <ActiveTasksSection
        runningTasks={runningTasks}
        completedTasks={completedTasks}
        failedTasks={failedTasks}
        activeTasksFilter={activeTasksFilter}
        activeTasksEntityFilter={activeTasksEntityFilter}
        onActiveTasksFilterChange={setActiveTasksFilter}
        onActiveTasksEntityFilterChange={setActiveTasksEntityFilter}
        onCancelRunningTasksByName={handleCancelRunningTasksByName}
      />

      <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <div className='flex items-center justify-between'>
            <h2 className='text-lg font-semibold text-gray-900'>
              Task History
            </h2>
            <div className='flex items-center gap-4'>
              <SearchInput
                onSearch={setSearchQuery}
                initialValue={searchQuery}
                placeholder='Search tasks...'
                className='w-64'
              />
              <select
                value={historyFilter}
                onChange={e => setHistoryFilter(e.target.value as TaskStatus)}
                className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              >
                <option value='all'>All Status</option>
                <option value='running'>Running</option>
                <option value='completed'>Completed</option>
                <option value='failed'>Failed</option>
                <option value='pending'>Pending</option>
              </select>
              <select
                value={historyTypeFilter}
                onChange={e => setHistoryTypeFilter(e.target.value as TaskType)}
                className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              >
                <option value='all'>All Types</option>
                <option value='sync'>Sync</option>
                <option value='download'>Download</option>
                <option value='fetch'>Fetch</option>
              </select>
              <select
                value={historyEntityFilter}
                onChange={e =>
                  setHistoryEntityFilter(e.target.value as EntityType)
                }
                className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              >
                <option value='all'>All Entities</option>
                <option value='artist'>Artist</option>
                <option value='album'>Album</option>
                <option value='playlist'>Playlist</option>
              </select>
              <PageSizeSelector
                pageSize={pageSize}
                onPageSizeChange={setPageSize}
                options={[20, 50, 100]}
              />
            </div>
          </div>
        </div>

        <div className='p-6'>
          {historyLoading ? (
            <div className='text-center py-8'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto' />
              <p className='mt-2 text-gray-600'>
                {isHistoryRefreshing
                  ? 'Refreshing task history...'
                  : 'Loading task history...'}
              </p>
            </div>
          ) : historyError ? (
            <div className='text-center py-8 text-red-600'>
              <p>Error loading task history: {historyError.message}</p>
            </div>
          ) : historyData?.taskHistory?.edges?.length === 0 ? (
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
                    {historyData?.taskHistory?.edges?.map(
                      (edge: {
                        node: {
                          id: string;
                          taskId: string;
                          type: string;
                          entityType: string;
                          entityId: string;
                          status: string;
                          startedAt: string;
                          completedAt: string | null;
                          progressPercentage: number | null;
                          durationSeconds: number | null;
                          logMessages: string[];
                        };
                      }) => {
                        const task = edge.node;
                        const isLogsOpen = !!expandedHistoryLogs[task.id];
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
                              <td className='px-3 py-2 whitespace-nowrap text-gray-700'>
                                {new Date(task.startedAt).toLocaleTimeString()}
                              </td>
                              <td className='px-3 py-2 whitespace-nowrap text-gray-700'>
                                {task.completedAt
                                  ? new Date(
                                      task.completedAt
                                    ).toLocaleTimeString()
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
                                {task.logMessages &&
                                task.logMessages.length > 0 ? (
                                  <button
                                    type='button'
                                    className='text-indigo-600 hover:underline text-sm'
                                    onClick={() =>
                                      setExpandedHistoryLogs(prev => ({
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
                      }
                    )}
                  </tbody>
                </table>
              </div>
              {historyData?.taskHistory?.pageInfo?.hasNextPage && (
                <LoadMoreButton
                  hasNextPage={historyData.taskHistory.pageInfo.hasNextPage}
                  loading={historyLoading}
                  remainingCount={
                    historyData.taskHistory.totalCount -
                    historyData.taskHistory.edges.length
                  }
                  onLoadMore={() =>
                    fetchMore({
                      variables: {
                        after: historyData.taskHistory.pageInfo.endCursor,
                      },
                    })
                  }
                />
              )}
            </div>
          )}
        </div>
      </div>

      <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <h2 className='text-lg font-semibold text-gray-900'>Task Logs</h2>
        </div>

        <div className='p-6'>
          {historyData?.taskHistory?.edges?.some(
            (edge: TaskHistoryEdge) => (edge.node.logMessages?.length ?? 0) > 0
          ) ? (
            <div className='space-y-1'>
              {historyData.taskHistory.edges
                .filter(
                  (edge: TaskHistoryEdge) =>
                    (edge.node.logMessages?.length ?? 0) > 0
                )
                .map((edge: TaskHistoryEdge) => {
                  const task = edge.node;
                  const isExpanded = !!expandedLogs[task.id];
                  return (
                    <div
                      key={task.id}
                      className='border border-gray-200 rounded p-2'
                    >
                      <div className='flex items-center justify-between gap-3'>
                        <div className='flex items-center gap-2 text-sm min-w-0 flex-1'>
                          <span className='font-medium text-gray-900 whitespace-nowrap'>
                            {task.type.charAt(0).toUpperCase() +
                              task.type.slice(1)}
                          </span>
                          <div className='min-w-0 flex-1'>
                            <EnhancedEntityDisplay
                              entityType={task.entityType}
                              entityId={task.entityId}
                              compact={true}
                            />
                          </div>
                          {!isExpanded && task.logMessages && (
                            <span className='text-xs text-gray-500 whitespace-nowrap flex-shrink-0'>
                              ({task.logMessages.length} logs)
                            </span>
                          )}
                        </div>
                        <button
                          type='button'
                          onClick={() =>
                            setExpandedLogs(prev => ({
                              ...prev,
                              [task.id]: !isExpanded,
                            }))
                          }
                          aria-expanded={isExpanded}
                          className='text-xs text-indigo-600 hover:underline px-2 py-1 rounded hover:bg-indigo-50'
                        >
                          {isExpanded ? 'Hide' : 'Show logs'}
                        </button>
                      </div>
                      {isExpanded && (
                        <div className='mt-2 bg-gray-50 rounded p-2 text-xs font-mono text-gray-700 max-h-32 overflow-y-auto'>
                          {task.logMessages?.map((log: string, idx: number) => (
                            <div
                              // eslint-disable-next-line react/no-array-index-key
                              key={`task-${task.id}-log-${idx}`}
                              className='mb-1'
                            >
                              {log}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>
          ) : (
            <div className='text-center py-8 text-gray-500'>
              <div className='text-4xl mb-4'>📝</div>
              <p>No task logs available</p>
              <p className='text-sm'>
                Logs will appear here when tasks are executed
              </p>
            </div>
          )}
        </div>
      </div>
      <ConfirmDialog />
    </div>
  );
}

export const Route = createFileRoute('/tasks')({
  component: Tasks,
});
