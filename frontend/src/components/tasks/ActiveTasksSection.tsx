import type { TaskHistory } from '../../types/generated/graphql';
import type { TaskType, EntityType } from '../../types/shared';
import { TaskCard } from './TaskCard';

interface ActiveTasksSectionProps {
  runningTasks: TaskHistory[];
  completedTasks: TaskHistory[];
  failedTasks: TaskHistory[];
  activeTasksFilter: TaskType;
  activeTasksEntityFilter: EntityType;
  onActiveTasksFilterChange: (filter: TaskType) => void;
  onActiveTasksEntityFilterChange: (filter: EntityType) => void;
  onCancelRunningTasksByName: (taskName: string) => void;
}

export function ActiveTasksSection({
  runningTasks,
  completedTasks,
  failedTasks,
  activeTasksFilter,
  activeTasksEntityFilter,
  onActiveTasksFilterChange,
  onActiveTasksEntityFilterChange,
  onCancelRunningTasksByName,
}: ActiveTasksSectionProps) {
  return (
    <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
      <div className='px-6 py-4 border-b border-gray-200'>
        <div className='flex items-center justify-between'>
          <h2 className='text-lg font-semibold text-gray-900'>Active Tasks</h2>
          <div className='flex items-center gap-4'>
            <select
              value={activeTasksFilter}
              onChange={e =>
                onActiveTasksFilterChange(e.target.value as TaskType)
              }
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
                onActiveTasksEntityFilterChange(e.target.value as EntityType)
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
        {runningTasks.length === 0 ? (
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
                    onClick={() => onCancelRunningTasksByName('all')}
                    className='px-3 py-1 bg-orange-500 text-white rounded text-sm hover:bg-orange-600'
                  >
                    Cancel All Running
                  </button>
                </div>
                <div className='space-y-2'>
                  {runningTasks.map((task: TaskHistory) => (
                    <TaskCard key={task.id} task={task} status='running' />
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
                    <TaskCard key={task.id} task={task} status='completed' />
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
                    <TaskCard key={task.id} task={task} status='failed' />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
