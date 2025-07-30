import React from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@apollo/client';
import { useState } from 'react';
import { SearchInput } from '../components/ui/SearchInput';
import { PageSizeSelector } from '../components/ui/PageSizeSelector';
import { LoadMoreButton } from '../components/ui/LoadMoreButton';
import {
  GetTaskHistoryDocument,
  GetActiveTasksDocument,
  type TaskHistory,
} from '../types/generated/graphql';
import { useMutation, gql } from '@apollo/client';

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

  // Query for real active tasks from the database
  const { data: activeTasksData } = useQuery(GetActiveTasksDocument, {
    variables: {
      first: 50, // Get more active tasks
    },
    fetchPolicy: 'cache-and-network',
    pollInterval: 5000, // Poll every 5 seconds for active tasks
  });

  // Get real active tasks from the database
  const realActiveTasks = activeTasksData?.activeTasks?.edges || [];

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

  // Cleanup stuck tasks mutation
  const [cleanupStuckTasks] = useMutation(gql`
    mutation CleanupStuckTasks {
      cleanupStuckTasks {
        success
        message
        cleanedCount
      }
    }
  `);

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
              // Refetch active tasks and history
              if (activeTasksData) {
                window.location.reload();
              }
            }}
            className='px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm mr-2'
          >
            Refresh
          </button>
          <button
            onClick={async () => {
              try {
                const result = await cleanupStuckTasks();
                if (result.data?.cleanupStuckTasks?.success) {
                  alert(
                    `Cleanup completed: ${result.data.cleanupStuckTasks.message}`
                  );
                  window.location.reload();
                } else {
                  alert(
                    'Cleanup failed: ' +
                      (result.data?.cleanupStuckTasks?.message ||
                        'Unknown error')
                  );
                }
              } catch (error) {
                alert('Error running cleanup: ' + error);
              }
            }}
            className='px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 text-sm'
          >
            Cleanup Stuck Tasks
          </button>
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
                        <div className='flex items-center gap-2'>
                          <span className='inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800'>
                            Running
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recently Completed Tasks */}
              {completedTasks.length > 0 && (
                <div>
                  <h3 className='text-sm font-medium text-gray-700 mb-3'>
                    Recently Completed ({completedTasks.length})
                  </h3>
                  <div className='space-y-2'>
                    {completedTasks.slice(-5).map((task: TaskHistory) => (
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
                              {new Date(task.startedAt).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        <div className='flex items-center gap-2'>
                          <span className='inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800'>
                            Completed
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recently Failed Tasks */}
              {failedTasks.length > 0 && (
                <div>
                  <h3 className='text-sm font-medium text-gray-700 mb-3'>
                    Recently Failed ({failedTasks.length})
                  </h3>
                  <div className='space-y-2'>
                    {failedTasks.slice(-5).map((task: TaskHistory) => (
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
                              {new Date(task.startedAt).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        <div className='flex items-center gap-2'>
                          <span className='inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800'>
                            Failed
                          </span>
                        </div>
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
            </div>
          </div>
        </div>

        <div className='p-6'>
          {historyLoading ? (
            <div className='text-center py-8'>
              <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto' />
              <p className='text-gray-500 mt-2'>Loading task history...</p>
            </div>
          ) : historyError ? (
            <div className='text-center py-8 text-red-500'>
              <p>Error loading task history: {historyError.message}</p>
            </div>
          ) : !historyData?.taskHistory?.edges?.length ? (
            <div className='text-center py-8 text-gray-500'>
              <div className='text-4xl mb-4'>📊</div>
              <p>No task history found</p>
              <p className='text-sm'>
                Tasks will appear here once they complete
              </p>
            </div>
          ) : (
            <div className='space-y-4'>
              {historyData.taskHistory.edges.map((task: TaskHistory) => (
                <div
                  key={task.id}
                  className='flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200'
                >
                  <div className='flex items-center gap-3'>
                    <div
                      className={`w-2 h-2 rounded-full ${
                        task.status === 'COMPLETED'
                          ? 'bg-green-500'
                          : task.status === 'FAILED'
                            ? 'bg-red-500'
                            : task.status === 'RUNNING'
                              ? 'bg-blue-500 animate-pulse'
                              : 'bg-gray-400'
                      }`}
                    />
                    <div>
                      <div className='font-medium text-gray-900'>
                        {task.type.charAt(0).toUpperCase() + task.type.slice(1)}{' '}
                        {task.entityType} {task.entityId}
                      </div>
                      <div className='text-sm text-gray-600'>
                        Started {new Date(task.startedAt).toLocaleString()}
                        {task.completedAt &&
                          ` • Completed ${new Date(task.completedAt).toLocaleString()}`}
                      </div>
                      {task.errorMessage && (
                        <div className='text-sm text-red-600 mt-1'>
                          Error: {task.errorMessage}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className='flex items-center gap-2'>
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        task.status === 'COMPLETED'
                          ? 'bg-green-100 text-green-800'
                          : task.status === 'FAILED'
                            ? 'bg-red-100 text-red-800'
                            : task.status === 'RUNNING'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {task.status}
                    </span>
                    {task.progressPercentage !== null && (
                      <span className='text-sm text-gray-500'>
                        {Math.round(task.progressPercentage)}%
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {historyData?.taskHistory?.pageInfo?.hasNextPage && (
            <div className='flex items-center justify-between mt-6'>
              <PageSizeSelector
                pageSize={pageSize}
                onPageSizeChange={setPageSize}
                options={[25, 50, 100]}
              />
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
          {historyData?.taskHistory?.edges?.length > 0 ? (
            <div className='space-y-4'>
              {historyData.taskHistory.edges
                .slice(0, 10)
                .map((task: TaskHistory) => (
                  <div
                    key={task.id}
                    className='border border-gray-200 rounded-lg p-4'
                  >
                    <div className='flex items-center justify-between mb-3'>
                      <div>
                        <h3 className='font-medium text-gray-900'>
                          {task.type.charAt(0).toUpperCase() +
                            task.type.slice(1)}{' '}
                          {task.entityType} {task.entityId}
                        </h3>
                        <p className='text-sm text-gray-500'>
                          Started: {new Date(task.startedAt).toLocaleString()}
                          {task.completedAt &&
                            ` • Completed: ${new Date(task.completedAt).toLocaleString()}`}
                        </p>
                      </div>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          task.status === 'COMPLETED'
                            ? 'bg-green-100 text-green-800'
                            : task.status === 'FAILED'
                              ? 'bg-red-100 text-red-800'
                              : task.status === 'RUNNING'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {task.status}
                      </span>
                    </div>

                    {task.logMessages && task.logMessages.length > 0 ? (
                      <div className='bg-gray-50 rounded p-3'>
                        <h4 className='text-sm font-medium text-gray-700 mb-2'>
                          Log Messages:
                        </h4>
                        <div className='space-y-1 max-h-32 overflow-y-auto'>
                          {task.logMessages.map(log => (
                            <div
                              key={`${log.timestamp}-${log.message.slice(0, 20)}`}
                              className='text-xs font-mono bg-white p-2 rounded border'
                            >
                              <span className='text-gray-500'>
                                {new Date(log.timestamp).toLocaleTimeString()}
                              </span>
                              <span className='ml-2 text-gray-700'>
                                {log.message}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className='text-sm text-gray-500 italic'>
                        No log messages available
                      </p>
                    )}

                    {task.errorMessage && (
                      <div className='mt-3 p-3 bg-red-50 border border-red-200 rounded'>
                        <h4 className='text-sm font-medium text-red-700 mb-1'>
                          Error:
                        </h4>
                        <p className='text-sm text-red-600'>
                          {task.errorMessage}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
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
