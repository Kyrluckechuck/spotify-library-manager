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
