import { gql } from '@apollo/client';

export const GetTaskHistoryDocument = gql`
  query GetTaskHistory(
    $first: Int = 20
    $after: String
    $status: String
    $type: String
    $entityType: String
    $search: String
  ) {
    taskHistory(
      first: $first
      after: $after
      status: $status
      type: $type
      entityType: $entityType
      search: $search
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        id
        taskId
        type
        entityId
        entityType
        status
        startedAt
        completedAt
        errorMessage
        durationSeconds
        progressPercentage
        logMessages {
          timestamp
          message
        }
      }
    }
  }
`;

export const GetActiveTasksDocument = gql`
  query GetActiveTasks($first: Int = 20, $after: String) {
    activeTasks(first: $first, after: $after) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        id
        taskId
        type
        entityId
        entityType
        status
        startedAt
        completedAt
        errorMessage
        durationSeconds
        progressPercentage
        logMessages {
          timestamp
          message
        }
      }
    }
  }
`;

export const CleanupStuckTasksDocument = gql`
  mutation CleanupStuckTasks {
    cleanupStuckTasks {
      success
      message
      cleanedCount
    }
  }
`;
