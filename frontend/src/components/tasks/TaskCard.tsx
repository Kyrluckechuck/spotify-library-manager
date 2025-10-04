import EnhancedEntityDisplay from '../EnhancedEntityDisplay';
import type { TaskHistory } from '../../types/generated/graphql';

type TaskStatus = 'running' | 'completed' | 'failed';

interface TaskCardProps {
  task: TaskHistory;
  status: TaskStatus;
}

const statusConfig: Record<
  TaskStatus,
  {
    bgColor: string;
    borderColor: string;
    dotColor: string;
    label: string;
    animate: boolean;
  }
> = {
  running: {
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    dotColor: 'bg-blue-500',
    label: 'Started',
    animate: true,
  },
  completed: {
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    dotColor: 'bg-green-500',
    label: 'Completed',
    animate: false,
  },
  failed: {
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    dotColor: 'bg-red-500',
    label: 'Failed',
    animate: false,
  },
};

export function TaskCard({ task, status }: TaskCardProps) {
  const config = statusConfig[status];

  const timestamp =
    status === 'running' ? task.startedAt : task.completedAt || task.startedAt;

  return (
    <div
      className={`flex items-center justify-between p-3 ${config.bgColor} rounded-lg border ${config.borderColor}`}
    >
      <div className='flex items-center gap-3'>
        <div
          className={`w-2 h-2 ${config.dotColor} rounded-full ${
            config.animate ? 'animate-pulse' : ''
          }`}
        />
        <div>
          <div className='font-medium text-gray-900'>
            {task.type.charAt(0).toUpperCase() + task.type.slice(1)}{' '}
            <EnhancedEntityDisplay
              entityType={task.entityType}
              entityId={task.entityId}
            />
          </div>
          <div className='text-sm text-gray-600'>
            {config.label} {new Date(timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
      {status === 'running' && task.progressPercentage !== null && (
        <div className='text-sm text-gray-600'>
          {task.progressPercentage}% complete
        </div>
      )}
      {(status === 'completed' || status === 'failed') &&
        task.durationSeconds && (
          <div className='text-sm text-gray-600'>{task.durationSeconds}s</div>
        )}
    </div>
  );
}
