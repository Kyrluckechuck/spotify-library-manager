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
