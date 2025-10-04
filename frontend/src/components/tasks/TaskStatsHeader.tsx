import { InlineSpinner } from '../ui/InlineSpinner';

interface TaskStatsHeaderProps {
  runningTasksCount: number;
  completedTodayCount: number;
  failedTodayCount: number;
  successRate: number;
  queueLoading: boolean;
  onRefresh: () => void;
}

export function TaskStatsHeader({
  runningTasksCount,
  completedTodayCount,
  failedTodayCount,
  successRate,
  queueLoading,
  onRefresh,
}: TaskStatsHeaderProps) {
  return (
    <>
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
              {runningTasksCount} active tasks
            </span>
            {queueLoading && <InlineSpinner label='Refreshing queue…' />}
            <span className='text-xs text-gray-500'>
              (auto-refreshing every 5s)
            </span>
          </div>
          <button
            onClick={onRefresh}
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
                {runningTasksCount}
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
                {completedTodayCount}
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
                {failedTodayCount}
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
              <p className='text-2xl font-bold text-gray-900'>{successRate}%</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
