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
        node {
          id
          taskId
          type
          entityId
          entityType
          status
          startedAt
          completedAt
          durationSeconds
          progressPercentage
          logMessages
        }
        cursor
      }
    }
  }
`;
