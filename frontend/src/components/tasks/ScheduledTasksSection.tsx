import { useMutation } from '@apollo/client/react';
import { useCallback } from 'react';
import type { PeriodicTask } from '../../types/generated/graphql';
import {
  GetPeriodicTasksDocument,
  RunPeriodicTaskNowDocument,
  SetPeriodicTaskEnabledDocument,
} from '../../types/generated/graphql';
import { useToast } from '../ui/useToast';

interface ScheduledTasksSectionProps {
  tasks: PeriodicTask[];
  loading: boolean;
}

function formatRelativeTime(dateStr: string | null | undefined): string {
  if (!dateStr) return 'Never';

  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

function formatTaskName(taskPath: string): string {
  // Extract the task function name from the full path
  // e.g., "library_manager.tasks.sync_tracked_playlists" -> "sync_tracked_playlists"
  const parts = taskPath.split('.');
  const funcName = parts[parts.length - 1];
  // Convert snake_case to Title Case
  return funcName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

interface RunNowButtonProps {
  task: PeriodicTask;
  onRunNow: (taskId: number, taskName: string) => void;
  isRunning: boolean;
}

function RunNowButton({ task, onRunNow, isRunning }: RunNowButtonProps) {
  return (
    <button
      type='button'
      onClick={() => onRunNow(task.id, task.name)}
      disabled={isRunning || !task.enabled}
      className={`
        px-3 py-1 text-xs font-medium rounded-md transition-colors
        ${
          task.enabled
            ? 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }
        ${isRunning ? 'opacity-50 cursor-wait' : ''}
      `}
      title={task.enabled ? 'Run this task immediately' : 'Enable task to run'}
    >
      {isRunning ? 'Queuing...' : 'Run Now'}
    </button>
  );
}

interface TaskToggleProps {
  task: PeriodicTask;
  onToggle: (taskId: number, enabled: boolean) => void;
  isToggling: boolean;
}

function TaskToggle({ task, onToggle, isToggling }: TaskToggleProps) {
  if (task.isCore) {
    return (
      <div
        className='text-xs text-gray-400 italic'
        title='Core system task - cannot be disabled'
      >
        System
      </div>
    );
  }

  return (
    <button
      type='button'
      onClick={() => onToggle(task.id, !task.enabled)}
      disabled={isToggling}
      className={`
        relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
        transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
        ${task.enabled ? 'bg-indigo-600' : 'bg-gray-200'}
        ${isToggling ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      role='switch'
      aria-checked={task.enabled}
      aria-label={`${task.enabled ? 'Disable' : 'Enable'} ${task.name}`}
    >
      <span
        className={`
          pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0
          transition duration-200 ease-in-out
          ${task.enabled ? 'translate-x-5' : 'translate-x-0'}
        `}
      />
    </button>
  );
}

export function ScheduledTasksSection({
  tasks,
  loading,
}: ScheduledTasksSectionProps) {
  const toast = useToast();
  const [setTaskEnabled, { loading: isToggling }] = useMutation(
    SetPeriodicTaskEnabledDocument,
    {
      refetchQueries: [{ query: GetPeriodicTasksDocument }],
    }
  );
  const [runTaskNow, { loading: isRunning }] = useMutation(
    RunPeriodicTaskNowDocument
  );

  const handleToggle = useCallback(
    async (taskId: number, enabled: boolean) => {
      try {
        await setTaskEnabled({ variables: { taskId, enabled } });
        toast.success(`Task ${enabled ? 'enabled' : 'disabled'}`);
      } catch (error) {
        toast.error(
          `Failed to update task: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    },
    [setTaskEnabled, toast]
  );

  const handleRunNow = useCallback(
    async (taskId: number, taskName: string) => {
      try {
        const result = await runTaskNow({ variables: { taskId } });
        if (result.data?.runPeriodicTaskNow?.success) {
          toast.success(`"${taskName}" queued for immediate execution`);
        } else {
          toast.error(
            result.data?.runPeriodicTaskNow?.message || 'Failed to queue task'
          );
        }
      } catch (error) {
        toast.error(
          `Failed to run task: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    },
    [runTaskNow, toast]
  );

  // Separate core and non-core tasks, then by enabled status
  const coreTasks = tasks.filter(t => t.isCore);
  const userTasks = tasks.filter(t => !t.isCore);
  const enabledUserTasks = userTasks.filter(t => t.enabled);
  const disabledUserTasks = userTasks.filter(t => !t.enabled);

  return (
    <div className='bg-white rounded-lg shadow-sm border border-gray-200'>
      <div className='px-6 py-4 border-b border-gray-200'>
        <div className='flex items-center justify-between'>
          <h2 className='text-lg font-semibold text-gray-900'>
            Scheduled Tasks (Celery Beat)
          </h2>
          <span className='text-sm text-gray-600'>
            {loading
              ? 'Loading...'
              : `${enabledUserTasks.length + coreTasks.length} active, ${disabledUserTasks.length} disabled`}
          </span>
        </div>
      </div>

      <div className='p-6'>
        {tasks.length === 0 ? (
          <div className='text-center py-8 text-gray-500'>
            <div className='text-4xl mb-4'>📅</div>
            <p>No scheduled tasks configured</p>
            <p className='text-sm'>
              Periodic tasks will appear here when configured in Celery Beat
            </p>
          </div>
        ) : (
          <div className='space-y-3'>
            {/* User-controllable tasks */}
            {enabledUserTasks.map(task => (
              <div
                key={task.id}
                className='flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200'
              >
                <div className='flex-1 min-w-0'>
                  <div className='flex items-center gap-2'>
                    <span className='font-medium text-gray-900'>
                      {task.name}
                    </span>
                    <span className='px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700'>
                      Active
                    </span>
                  </div>
                  <div className='text-sm text-gray-600 mt-1'>
                    {formatTaskName(task.task)}
                  </div>
                  {task.description && (
                    <div className='text-xs text-gray-500 mt-1'>
                      {task.description}
                    </div>
                  )}
                </div>

                <div className='flex items-center gap-4 text-sm'>
                  <div className='text-right'>
                    <div className='text-gray-500'>Schedule</div>
                    <div className='font-medium text-gray-900'>
                      {task.scheduleDescription}
                    </div>
                  </div>
                  <div className='text-right'>
                    <div className='text-gray-500'>Last Run</div>
                    <div className='font-medium text-gray-900'>
                      {formatRelativeTime(task.lastRunAt)}
                    </div>
                  </div>
                  <div className='text-right'>
                    <div className='text-gray-500'>Total Runs</div>
                    <div className='font-medium text-gray-900'>
                      {task.totalRunCount}
                    </div>
                  </div>
                  <RunNowButton
                    task={task}
                    onRunNow={handleRunNow}
                    isRunning={isRunning}
                  />
                  <TaskToggle
                    task={task}
                    onToggle={handleToggle}
                    isToggling={isToggling}
                  />
                </div>
              </div>
            ))}

            {/* Disabled user tasks */}
            {disabledUserTasks.length > 0 && (
              <>
                <div className='text-sm font-medium text-gray-500 mt-4 pt-4 border-t'>
                  Disabled Tasks
                </div>
                {disabledUserTasks.map(task => (
                  <div
                    key={task.id}
                    className='flex items-center justify-between p-4 bg-gray-100 rounded-lg border border-gray-200 opacity-75'
                  >
                    <div className='flex-1 min-w-0'>
                      <div className='flex items-center gap-2'>
                        <span className='font-medium text-gray-700'>
                          {task.name}
                        </span>
                        <span className='px-2 py-0.5 text-xs rounded-full bg-gray-200 text-gray-600'>
                          Disabled
                        </span>
                      </div>
                      <div className='text-sm text-gray-500 mt-1'>
                        {formatTaskName(task.task)}
                      </div>
                    </div>
                    <div className='flex items-center gap-4 text-sm'>
                      <div className='text-gray-500'>
                        {task.scheduleDescription}
                      </div>
                      <RunNowButton
                        task={task}
                        onRunNow={handleRunNow}
                        isRunning={isRunning}
                      />
                      <TaskToggle
                        task={task}
                        onToggle={handleToggle}
                        isToggling={isToggling}
                      />
                    </div>
                  </div>
                ))}
              </>
            )}

            {/* Core system tasks */}
            {coreTasks.length > 0 && (
              <>
                <div className='text-sm font-medium text-gray-500 mt-4 pt-4 border-t'>
                  System Tasks
                </div>
                {coreTasks.map(task => (
                  <div
                    key={task.id}
                    className='flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-100'
                  >
                    <div className='flex-1 min-w-0'>
                      <div className='flex items-center gap-2'>
                        <span className='font-medium text-gray-900'>
                          {task.name}
                        </span>
                        <span className='px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700'>
                          System
                        </span>
                      </div>
                      <div className='text-sm text-gray-600 mt-1'>
                        {formatTaskName(task.task)}
                      </div>
                    </div>

                    <div className='flex items-center gap-4 text-sm'>
                      <div className='text-right'>
                        <div className='text-gray-500'>Schedule</div>
                        <div className='font-medium text-gray-900'>
                          {task.scheduleDescription}
                        </div>
                      </div>
                      <div className='text-right'>
                        <div className='text-gray-500'>Last Run</div>
                        <div className='font-medium text-gray-900'>
                          {formatRelativeTime(task.lastRunAt)}
                        </div>
                      </div>
                      <div className='text-right'>
                        <div className='text-gray-500'>Total Runs</div>
                        <div className='font-medium text-gray-900'>
                          {task.totalRunCount}
                        </div>
                      </div>
                      <RunNowButton
                        task={task}
                        onRunNow={handleRunNow}
                        isRunning={isRunning}
                      />
                      <TaskToggle
                        task={task}
                        onToggle={handleToggle}
                        isToggling={isToggling}
                      />
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
