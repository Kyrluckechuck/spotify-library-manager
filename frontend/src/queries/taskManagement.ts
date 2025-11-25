import { gql } from '@apollo/client';

export const GetQueueStatusDocument = gql`
  query GetQueueStatus {
    queueStatus {
      totalPendingTasks
      taskCounts {
        taskName
        count
      }
      queueSize
    }
  }
`;

export const CancelAllPendingTasksDocument = gql`
  mutation CancelAllPendingTasks {
    cancelAllPendingTasks {
      success
      message
    }
  }
`;

export const CancelTasksByNameDocument = gql`
  mutation CancelTasksByName($taskName: String!) {
    cancelTasksByName(taskName: $taskName) {
      success
      message
    }
  }
`;

export const CancelRunningTasksByNameDocument = gql`
  mutation CancelRunningTasksByName($taskName: String!) {
    cancelRunningTasksByName(taskName: $taskName) {
      success
      message
    }
  }
`;

export const CancelAllTasksDocument = gql`
  mutation CancelAllTasks {
    cancelAllTasks {
      success
      message
    }
  }
`;

export const GetPeriodicTasksDocument = gql`
  query GetPeriodicTasks($enabledOnly: Boolean) {
    periodicTasks(enabledOnly: $enabledOnly) {
      id
      name
      task
      enabled
      isCore
      description
      scheduleDescription
      lastRunAt
      totalRunCount
    }
  }
`;

export const SetPeriodicTaskEnabledDocument = gql`
  mutation SetPeriodicTaskEnabled($taskId: Int!, $enabled: Boolean!) {
    setPeriodicTaskEnabled(taskId: $taskId, enabled: $enabled) {
      id
      name
      enabled
      isCore
    }
  }
`;

export const RunPeriodicTaskNowDocument = gql`
  mutation RunPeriodicTaskNow($taskId: Int!) {
    runPeriodicTaskNow(taskId: $taskId) {
      success
      message
    }
  }
`;
