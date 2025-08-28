import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation } from '@apollo/client';
import { useState } from 'react';
import type { TaskCount } from '../types/common';
import { SearchInput } from '../components/ui/SearchInput';
import { InlineSpinner } from '../components/ui/InlineSpinner';
// import { useRequestState } from '../hooks/useRequestState';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import {
  GetTaskHistoryDocument,
  type TaskHistory,
} from '../types/generated/graphql';
import {
  GetQueueStatusDocument,
  CancelTasksByNameDocument,
  CancelRunningTasksByNameDocument,
  CancelAllTasksDocument,
} from '../queries/taskManagement';
import EnhancedEntityDisplay from '../components/EnhancedEntityDisplay';

type TaskStatus = 'running' | 'completed' | 'failed' | 'pending' | 'all';
type TaskType = 'sync' | 'download' | 'fetch' | 'all';
type EntityType = 'artist' | 'album' | 'playlist' | 'all';

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

  const [expandedLogs, setExpandedLogs] = useState<Record<number, boolean>>({});
  const [expandedHistoryLogs, setExpandedHistoryLogs] = useState<
    Record<number, boolean>
  >({});

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
    pollInterval: 8000,
  });

  const {
    data: queueData,
    loading: queueLoading,
    refetch: refetchQueue,
  } = useQuery(GetQueueStatusDocument, {
    pollInterval: 5000,
  });

  const historyNodes: TaskHistory[] =
    historyData?.taskHistory?.edges?.map(
      (edge: { node: TaskHistory }) => edge.node
    ) || [];

  const realActiveTasks = historyNodes.filter(
    (task: TaskHistory) => task.status === 'RUNNING'
  );

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

  const handleCancelAllTasks = async () => {
    if (
      confirm(
        'Are you sure you want to cancel all tasks (both pending and running)? This action cannot be undone.'
      )
    ) {
      try {
        const result = await cancelAllTasksEnhanced();
        if (result.data?.cancelAllTasks?.success) {
          alert('Successfully cancelled all tasks');
          refetchQueue();
        } else {
          alert(
            'Failed to cancel tasks: ' + result.data?.cancelAllTasks?.message
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

  const handleCancelRunningTasksByName = async (taskName: string) => {
    if (
      confirm(
        `Are you sure you want to cancel all running '${taskName}' tasks? This action cannot be undone.`
      )
    ) {
      try {
        const result = await cancelRunningTasksByName({
          variables: { taskName },
        });
        if (result.data?.cancelRunningTasksByName?.success) {
          alert(`Successfully cancelled running ${taskName} tasks`);
          refetchQueue();
        } else {
          alert(
            'Failed to cancel running tasks: ' +
              result.data?.cancelRunningTasksByName?.message
          );
        }
      } catch (error) {
        alert('Error cancelling running tasks: ' + error);
      }
    }
  };

  return (
    <div className='space-y-8'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold text-gray-900'>Background Tasks</h1>
          <p className='text-gray-600 mt-2'>
            Monitor active processes and view task history
          </p>
        </div>
        <div className='flex items-center gap-4'>
          <div className='flex items-center gap-3 text-sm text-blue-600'>
            <span className='flex items-center gap-2'>
              <span className='w-2 h-2 bg-blue-500 rounded-full animate-pulse' />
              {runningTasks.length} active tasks
            </span>
            {queueLoading && <InlineSpinner label='Refreshing queue…' />}
            <span className='text-xs text-gray-500'>
              (auto-refreshing every 5s)
            </span>
          </div>
          <button
            onClick={() => {
              window.location.reload();
            }}
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm'
          >
            Refresh
          </button>
        </div>
      </div>

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
                {
                  historyNodes.filter(
                    (task: TaskHistory) =>
                      task.status === 'COMPLETED' &&
                      !!task.completedAt &&
                      new Date(task.completedAt).toDateString() ===
                        new Date().toDateString()
                  ).length
                }
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
                {
                  historyNodes.filter(
                    (task: TaskHistory) =>
                      task.status === 'FAILED' &&
                      !!task.completedAt &&
                      new Date(task.completedAt).toDateString() ===
                        new Date().toDateString()
                  ).length
                }
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
                  const completed = historyNodes.filter(
                    (task: TaskHistory) => task.status === 'COMPLETED'
                  ).length;
                  const failed = historyNodes.filter(
                    (task: TaskHistory) => task.status === 'FAILED'
                  ).length;
                  const total = completed + failed;
                  return total > 0 ? Math.round((completed / total) * 100) : 0;
                })()}
                %
              </p>
            </div>
          </div>
        </div>
      </div>

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

              <div className='flex justify-center pt-4 border-t border-gray-200'>
                <button
                  onClick={handleCancelAllTasks}
                  className='px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium'
                >
                  Cancel All Tasks (Pending & Running)
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

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
              {runningTasks.length > 0 && (
                <div>
                  <div className='flex items-center justify-between mb-3'>
                    <h3 className='text-sm font-medium text-gray-700'>
                      Running ({runningTasks.length})
                    </h3>
                    <button
                      onClick={() => handleCancelRunningTasksByName('all')}
                      className='px-3 py-1 bg-orange-500 text-white rounded text-sm hover:bg-orange-600'
                    >
                      Cancel All Running
                    </button>
                  </div>
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
                              <EnhancedEntityDisplay
                                entityType={task.entityType}
                                entityId={task.entityId}
                              />
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
                              <EnhancedEntityDisplay
                                entityType={task.entityType}
                                entityId={task.entityId}
                              />
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
                              <EnhancedEntityDisplay
                                entityType={task.entityType}
                                entityId={task.entityId}
                              />
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
                          id: number;
                          taskId: string;
                          type: string;
                          entityType: string;
                          entityId: string;
                          status: string;
                          startedAt: string;
                          completedAt?: string;
                          progressPercentage?: number;
                          durationSeconds?: number;
                          logMessages?: string[];
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
                                    {task.logMessages.map((log: string) => (
                                      <div
                                        key={`task-${task.id}-log-row-${log}`}
                                        className='mb-1'
                                      >
                                        {log}
                                      </div>
                                    ))}
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
            (edge: { node: { logMessages?: string[] } }) =>
              (edge.node.logMessages?.length ?? 0) > 0
          ) ? (
            <div className='space-y-1'>
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
                            {task.logMessages?.map((log: string) => (
                              <div
                                key={`task-${task.id}-log-entry-${log}`}
                                className='mb-1'
                              >
                                {log}
                              </div>
                            ))}
                          </div>
                        )}
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
    </div>
  );
}

export const Route = createFileRoute('/tasks')({
  component: Tasks,
});
