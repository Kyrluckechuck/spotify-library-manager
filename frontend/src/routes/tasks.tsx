import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { useState } from 'react';
import type { TaskCount } from '../types/common';
import { SearchInput } from '../components/ui/SearchInput';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import {
  GetTaskHistoryDocument,
  type TaskHistory,
} from '../types/generated/graphql';
import {
  GetQueueStatusDocument,
  CancelAllPendingTasksDocument,
  CancelTasksByNameDocument,
} from '../queries/taskManagement';

type TaskStatus = 'running' | 'completed' | 'failed' | 'pending' | 'all';
type TaskType = 'sync' | 'download' | 'fetch' | 'all';
type EntityType = 'artist' | 'album' | 'playlist' | 'all';

function Tasks() {
  // State for active tasks view
  const [activeTasksFilter, setActiveTasksFilter] = useState<TaskType>('all');
  const [activeTasksEntityFilter, setActiveTasksEntityFilter] =
    useState<EntityType>('all');

  // State for task history view
  const [historyFilter, setHistoryFilter] = useState<TaskStatus>('all');
  const [historyTypeFilter, setHistoryTypeFilter] = useState<TaskType>('all');
  const [historyEntityFilter, setHistoryEntityFilter] =
    useState<EntityType>('all');
  const [pageSize, setPageSize] = useState(50);
  const [searchQuery, setSearchQuery] = useState('');

  // Task cancellation mutations
  const [cancelAllTasks] = useMutation(CancelAllPendingTasksDocument);
  const [cancelTasksByName] = useMutation(CancelTasksByNameDocument);

  const {
    data: historyData,
    loading: historyLoading,
    error: historyError,
    fetchMore,
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
    notifyOnNetworkStatusChange: false,
    pollInterval: 8000, // Poll every 8 seconds for task history updates
  });

  // Queue status query
  const {
    data: queueData,
    loading: queueLoading,
    refetch: refetchQueue,
  } = useQuery(GetQueueStatusDocument, {
    pollInterval: 5000, // Poll every 5 seconds for queue updates
  });

  // Get active tasks from the task history
  const realActiveTasks =
    historyData?.taskHistory?.edges?.filter(
      (task: TaskHistory) => task.status === 'RUNNING'
    ) || [];

  // Filter active tasks
  const filteredActiveTasks = realActiveTasks.filter((task: TaskHistory) => {
    if (
      activeTasksFilter !== 'all' &&
      task.type.toLowerCase() !== activeTasksFilter
    )
      return false;
    if (
      activeTasksEntityFilter !== 'all' &&
      task.entityType.toLowerCase() !== activeTasksEntityFilter
    )
      return false;
    return true;
  });

  const runningTasks = filteredActiveTasks.filter(
    (task: TaskHistory) => task.status === 'RUNNING'
  );
  const completedTasks = filteredActiveTasks.filter(
    (task: TaskHistory) => task.status === 'COMPLETED'
  );
  const failedTasks = filteredActiveTasks.filter(
    (task: TaskHistory) => task.status === 'FAILED'
  );

  // Handle task cancellation
  const handleCancelAllTasks = async () => {
    if (
      confirm(
        'Are you sure you want to cancel all pending tasks? This action cannot be undone.'
      )
    ) {
      try {
        const result = await cancelAllTasks();
        if (result.data?.cancelAllPendingTasks?.success) {
          alert('Successfully cancelled all pending tasks');
          refetchQueue();
        } else {
          alert(
            'Failed to cancel tasks: ' +
              result.data?.cancelAllPendingTasks?.message
          );
        }
      } catch (error) {
        alert('Error cancelling tasks: ' + error);
      }
    }
  };

  const handleCancelTasksByName = async (taskName: string) => {
    if (
      confirm(
        `Are you sure you want to cancel all '${taskName}' tasks? This action cannot be undone.`
      )
    ) {
      try {
        const result = await cancelTasksByName({ variables: { taskName } });
        if (result.data?.cancelTasksByName?.success) {
          alert(`Successfully cancelled ${taskName} tasks`);
          refetchQueue();
        } else {
          alert(
            'Failed to cancel tasks: ' + result.data?.cancelTasksByName?.message
          );
        }
      } catch (error) {
        alert('Error cancelling tasks: ' + error);
      }
    }
  };

  return (
    <div className='space-y-8'>
      {/* Page Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold text-gray-900'>Background Tasks</h1>
          <p className='text-gray-600 mt-2'>
            Monitor active processes and view task history
          </p>
        </div>
        <div className='flex items-center gap-4'>
          <div className='flex items-center gap-2 text-sm text-blue-600'>
            <div className='w-2 h-2 bg-blue-500 rounded-full animate-pulse' />
            <span>{runningTasks.length} active tasks</span>
            <span className='text-xs text-gray-500'>
              (auto-refreshing every 5s)
            </span>
          </div>
          <button
            onClick={() => {
              // Refetch task history
              window.location.reload();
            }}
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm'
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Huey Queue Management Section */}
      <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <div className='flex items-center justify-between'>
            <h2 className='text-lg font-semibold text-gray-900'>
              Huey Queue Management
            </h2>
            <div className='flex items-center gap-2'>
              <span className='text-sm text-gray-600'>
                {queueLoading
                  ? 'Loading...'
                  : `${queueData?.queueStatus?.totalPendingTasks || 0} pending tasks`}
              </span>
            </div>
          </div>
        </div>

        <div className='p-6'>
          {queueData?.queueStatus?.totalPendingTasks === 0 ? (
            <div className='text-center py-8 text-gray-500'>
              <div className='text-4xl mb-4'>✅</div>
              <p>No pending tasks in Huey queue</p>
              <p className='text-sm'>
                All tasks are either running or completed
              </p>
            </div>
          ) : (
            <div className='space-y-4'>
              {/* Task Counts */}
              <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
                {queueData?.queueStatus?.taskCounts?.map(
                  (taskCount: TaskCount) => (
                    <div
                      key={taskCount.taskName}
                      className='flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200'
                    >
                      <div>
                        <div className='font-medium text-gray-900'>
                          {taskCount.taskName}
                        </div>
                        <div className='text-sm text-gray-600'>
                          {taskCount.count} pending
                        </div>
                      </div>
                      <button
                        onClick={() =>
                          handleCancelTasksByName(taskCount.taskName)
                        }
                        className='px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600'
                      >
                        Cancel
                      </button>
                    </div>
                  )
                )}
              </div>

              {/* Cancel All Button */}
              <div className='flex justify-center pt-4 border-t border-gray-200'>
                <button
                  onClick={handleCancelAllTasks}
                  className='px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium'
                >
                  Cancel All Pending Tasks
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Active Tasks Section */}
      <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <div className='flex items-center justify-between'>
            <h2 className='text-lg font-semibold text-gray-900'>
              Active Tasks
            </h2>
            <div className='flex items-center gap-4'>
              <select
                value={activeTasksFilter}
                onChange={e => setActiveTasksFilter(e.target.value as TaskType)}
                className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              >
                <option value='all'>All Types</option>
                <option value='sync'>Sync</option>
                <option value='download'>Download</option>
                <option value='fetch'>Fetch</option>
              </select>
              <select
                value={activeTasksEntityFilter}
                onChange={e =>
                  setActiveTasksEntityFilter(e.target.value as EntityType)
                }
                className='px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500'
              >
                <option value='all'>All Entities</option>
                <option value='artist'>Artist</option>
                <option value='album'>Album</option>
                <option value='playlist'>Playlist</option>
              </select>
            </div>
          </div>
        </div>

        <div className='p-6'>
          {filteredActiveTasks.length === 0 ? (
            <div className='text-center py-8 text-gray-500'>
              <div className='text-4xl mb-4'>📋</div>
              <p>No active tasks found</p>
              <p className='text-sm'>
                Tasks will appear here when they start running
              </p>
            </div>
          ) : (
            <div className='space-y-4'>
              {/* Running Tasks */}
              {runningTasks.length > 0 && (
                <div>
                  <h3 className='text-sm font-medium text-gray-700 mb-3'>
                    Running ({runningTasks.length})
                  </h3>
                  <div className='space-y-2'>
                    {runningTasks.map((task: TaskHistory) => (
                      <div
                        key={task.id}
                        className='flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200'
                      >
                        <div className='flex items-center gap-3'>
                          <div className='w-2 h-2 bg-blue-500 rounded-full animate-pulse' />
                          <div>
                            <div className='font-medium text-gray-900'>
                              {task.type.charAt(0).toUpperCase() +
                                task.type.slice(1)}{' '}
                              {task.entityType} {task.entityId}
                            </div>
                            <div className='text-sm text-gray-600'>
                              Started{' '}
                              {new Date(task.startedAt).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        {task.progressPercentage !== null && (
                          <div className='text-sm text-gray-600'>
                            {task.progressPercentage}% complete
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Completed Tasks */}
              {completedTasks.length > 0 && (
                <div>
                  <h3 className='text-sm font-medium text-gray-700 mb-3'>
                    Completed ({completedTasks.length})
                  </h3>
                  <div className='space-y-2'>
                    {completedTasks.map((task: TaskHistory) => (
                      <div
                        key={task.id}
                        className='flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200'
                      >
                        <div className='flex items-center gap-3'>
                          <div className='w-2 h-2 bg-green-500 rounded-full' />
                          <div>
                            <div className='font-medium text-gray-900'>
                              {task.type.charAt(0).toUpperCase() +
                                task.type.slice(1)}{' '}
                              {task.entityType} {task.entityId}
                            </div>
                            <div className='text-sm text-gray-600'>
                              Completed{' '}
                              {task.completedAt
                                ? new Date(
                                    task.completedAt
                                  ).toLocaleTimeString()
                                : 'Recently'}
                            </div>
                          </div>
                        </div>
                        {task.durationSeconds && (
                          <div className='text-sm text-gray-600'>
                            {task.durationSeconds}s
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Failed Tasks */}
              {failedTasks.length > 0 && (
                <div>
                  <h3 className='text-sm font-medium text-gray-700 mb-3'>
                    Failed ({failedTasks.length})
                  </h3>
                  <div className='space-y-2'>
                    {failedTasks.map((task: TaskHistory) => (
                      <div
                        key={task.id}
                        className='flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200'
                      >
                        <div className='flex items-center gap-3'>
                          <div className='w-2 h-2 bg-red-500 rounded-full' />
                          <div>
                            <div className='font-medium text-gray-900'>
                              {task.type.charAt(0).toUpperCase() +
                                task.type.slice(1)}{' '}
                              {task.entityType} {task.entityId}
                            </div>
                            <div className='text-sm text-gray-600'>
                              Failed{' '}
                              {task.completedAt
                                ? new Date(
                                    task.completedAt
                                  ).toLocaleTimeString()
                                : 'Recently'}
                            </div>
                          </div>
                        </div>
                        {task.durationSeconds && (
                          <div className='text-sm text-gray-600'>
                            {task.durationSeconds}s
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Task History Section */}
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
              <p className='mt-2 text-gray-600'>Loading task history...</p>
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
            <div className='space-y-4'>
              {historyData?.taskHistory?.edges?.map(
                (edge: {
                  node: {
                    id: number;
                    type: string;
                    entityType: string;
                    entityId: string;
                    status: string;
                    startedAt: string;
                    completedAt?: string;
                    progressPercentage?: number;
                    durationSeconds?: number;
                  };
                }) => {
                  const task = edge.node;
                  return (
                    <div
                      key={task.id}
                      className={`flex items-center justify-between p-4 rounded-lg border ${
                        task.status === 'RUNNING'
                          ? 'bg-blue-50 border-blue-200'
                          : task.status === 'COMPLETED'
                            ? 'bg-green-50 border-green-200'
                            : task.status === 'FAILED'
                              ? 'bg-red-50 border-red-200'
                              : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className='flex items-center gap-4'>
                        <div
                          className={`w-3 h-3 rounded-full ${
                            task.status === 'RUNNING'
                              ? 'bg-blue-500 animate-pulse'
                              : task.status === 'COMPLETED'
                                ? 'bg-green-500'
                                : task.status === 'FAILED'
                                  ? 'bg-red-500'
                                  : 'bg-gray-400'
                          }`}
                        />
                        <div>
                          <div className='font-medium text-gray-900'>
                            {task.type.charAt(0).toUpperCase() +
                              task.type.slice(1)}{' '}
                            {task.entityType} {task.entityId}
                          </div>
                          <div className='text-sm text-gray-600'>
                            {task.status === 'RUNNING'
                              ? `Started ${new Date(
                                  task.startedAt
                                ).toLocaleTimeString()}`
                              : task.status === 'COMPLETED'
                                ? `Completed ${
                                    task.completedAt
                                      ? new Date(
                                          task.completedAt
                                        ).toLocaleTimeString()
                                      : 'Unknown time'
                                  }`
                                : task.status === 'FAILED'
                                  ? `Failed ${
                                      task.completedAt
                                        ? new Date(
                                            task.completedAt
                                          ).toLocaleTimeString()
                                        : 'Unknown time'
                                    }`
                                  : `Pending ${new Date(
                                      task.startedAt
                                    ).toLocaleTimeString()}`}
                          </div>
                        </div>
                      </div>
                      <div className='flex items-center gap-4 text-sm text-gray-600'>
                        {task.progressPercentage !== null && (
                          <span>{task.progressPercentage}%</span>
                        )}
                        {task.durationSeconds && (
                          <span>{task.durationSeconds}s</span>
                        )}
                      </div>
                    </div>
                  );
                }
              )}

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

      {/* Task Logs Section */}
      <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <h2 className='text-lg font-semibold text-gray-900'>Task Logs</h2>
        </div>

        <div className='p-6'>
          {historyData?.taskHistory?.edges?.some(
            (edge: { node: { logMessages?: string[] } }) =>
              (edge.node.logMessages?.length ?? 0) > 0
          ) ? (
            <div className='space-y-4'>
              {historyData.taskHistory.edges
                .filter(
                  (edge: { node: { logMessages?: string[] } }) =>
                    (edge.node.logMessages?.length ?? 0) > 0
                )
                .map(
                  (edge: {
                    node: {
                      id: number;
                      type: string;
                      entityType: string;
                      entityId: string;
                      logMessages?: string[];
                    };
                  }) => {
                    const task = edge.node;
                    return (
                      <div
                        key={task.id}
                        className='border border-gray-200 rounded-lg p-4'
                      >
                        <div className='font-medium text-gray-900 mb-2'>
                          {task.type.charAt(0).toUpperCase() +
                            task.type.slice(1)}{' '}
                          {task.entityType} {task.entityId}
                        </div>
                        <div className='bg-gray-50 rounded p-3 text-sm font-mono text-gray-700 max-h-32 overflow-y-auto'>
                          {task.logMessages?.map(
                            (log: string, index: number) => (
                              <div
                                key={`task-${task.id}-log-entry-${index}`}
                                className='mb-1'
                              >
                                {log}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    );
                  }
                )}
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

      {/* Statistics Dashboard */}
      <div className='grid grid-cols-1 md:grid-cols-4 gap-6'>
        <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-6'>
          <div className='flex items-center'>
            <div className='p-2 bg-blue-100 rounded-lg'>
              <div className='w-6 h-6 bg-blue-500 rounded-full animate-pulse' />
            </div>
            <div className='ml-4'>
              <p className='text-sm font-medium text-gray-600'>Active Tasks</p>
              <p className='text-2xl font-bold text-gray-900'>
                {runningTasks.length}
              </p>
            </div>
          </div>
        </div>

        <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-6'>
          <div className='flex items-center'>
            <div className='p-2 bg-green-100 rounded-lg'>
              <div className='w-6 h-6 bg-green-500 rounded-full' />
            </div>
            <div className='ml-4'>
              <p className='text-sm font-medium text-gray-600'>
                Completed Today
              </p>
              <p className='text-2xl font-bold text-gray-900'>
                {historyData?.taskHistory?.edges?.filter(
                  (task: TaskHistory) =>
                    task.status === 'COMPLETED' &&
                    new Date(task.startedAt).toDateString() ===
                      new Date().toDateString()
                ).length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-6'>
          <div className='flex items-center'>
            <div className='p-2 bg-red-100 rounded-lg'>
              <div className='w-6 h-6 bg-red-500 rounded-full' />
            </div>
            <div className='ml-4'>
              <p className='text-sm font-medium text-gray-600'>Failed Today</p>
              <p className='text-2xl font-bold text-gray-900'>
                {historyData?.taskHistory?.edges?.filter(
                  (task: TaskHistory) =>
                    task.status === 'FAILED' &&
                    new Date(task.startedAt).toDateString() ===
                      new Date().toDateString()
                ).length || 0}
              </p>
            </div>
          </div>
        </div>

        <div className='bg-white rounded-lg shadow-sm border border-gray-200 p-6'>
          <div className='flex items-center'>
            <div className='p-2 bg-purple-100 rounded-lg'>
              <div className='w-6 h-6 bg-purple-500 rounded-full' />
            </div>
            <div className='ml-4'>
              <p className='text-sm font-medium text-gray-600'>Success Rate</p>
              <p className='text-2xl font-bold text-gray-900'>
                {(() => {
                  const completed =
                    historyData?.taskHistory?.edges?.filter(
                      (task: TaskHistory) => task.status === 'COMPLETED'
                    ).length || 0;
                  const failed =
                    historyData?.taskHistory?.edges?.filter(
                      (task: TaskHistory) => task.status === 'FAILED'
                    ).length || 0;
                  const total = completed + failed;
                  return total > 0 ? Math.round((completed / total) * 100) : 0;
                })()}
                %
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/tasks')({
  component: Tasks,
});
