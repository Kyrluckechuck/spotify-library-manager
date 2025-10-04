import type { TaskCount } from '../../types/common';

interface QueueManagementSectionProps {
  queueLoading: boolean;
  totalPendingTasks: number;
  taskCounts: TaskCount[];
  onCancelTasksByName: (taskName: string) => void;
  onCancelAllTasks: () => void;
}

export function QueueManagementSection({
  queueLoading,
  totalPendingTasks,
  taskCounts,
  onCancelTasksByName,
  onCancelAllTasks,
}: QueueManagementSectionProps) {
  return (
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
                : `${totalPendingTasks} pending tasks`}
            </span>
          </div>
        </div>
      </div>

      <div className='p-6'>
        {totalPendingTasks === 0 ? (
          <div className='text-center py-8 text-gray-500'>
            <div className='text-4xl mb-4'>✅</div>
            <p>No pending tasks in Huey queue</p>
            <p className='text-sm'>All tasks are either running or completed</p>
          </div>
        ) : (
          <div className='space-y-4'>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
              {taskCounts.map((taskCount: TaskCount) => (
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
                    onClick={() => onCancelTasksByName(taskCount.taskName)}
                    className='px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600'
                  >
                    Cancel
                  </button>
                </div>
              ))}
            </div>

            <div className='flex justify-center pt-4 border-t border-gray-200'>
              <button
                onClick={onCancelAllTasks}
                className='px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium'
              >
                Cancel All Tasks (Pending & Running)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
