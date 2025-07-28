import { gql } from '@apollo/client';

export const DownloadUrlDocument = gql`
  mutation DownloadUrl($url: String!, $autoTrackArtists: Boolean!) {
    downloadUrl(url: $url, autoTrackArtists: $autoTrackArtists) {
      success
      message
      taskId
    }
  }
`;

export const CreatePlaylistDocument = gql`
  mutation CreatePlaylist($url: String!, $name: String!, $autoTrackArtists: Boolean!) {
    createPlaylist(url: $url, name: $name, autoTrackArtists: $autoTrackArtists) {
      success
      message
      playlist {
        id
        name
        url
        enabled
        autoTrackArtists
        lastSyncedAt
      }
    }
  }
`;

export const UpdatePlaylistDocument = gql`
  mutation UpdatePlaylist($playlistId: Int!, $name: String!, $autoTrackArtists: Boolean!) {
    updatePlaylist(playlistId: $playlistId, name: $name, autoTrackArtists: $autoTrackArtists) {
      success
      message
      playlist {
        id
        name
        url
        enabled
        autoTrackArtists
        lastSyncedAt
      }
    }
  }
`; 