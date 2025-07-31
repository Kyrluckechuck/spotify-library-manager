import { gql } from '@apollo/client';

export const DOWNLOAD_URL = gql`
  mutation DownloadUrl($url: String!, $autoTrackArtists: Boolean) {
    downloadUrl(url: $url, autoTrackArtists: $autoTrackArtists) {
      success
      message
      artist {
        id
        name
        gid
        isTracked
        addedAt
        lastSynced
      }
      album {
        id
        name
        spotifyGid
        totalTracks
        wanted
        downloaded
        albumType
        albumGroup
        artist
        artistId
      }
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

export const CREATE_PLAYLIST = gql`
  mutation CreatePlaylist(
    $name: String!
    $url: String!
    $autoTrackArtists: Boolean!
  ) {
    createPlaylist(
      name: $name
      url: $url
      autoTrackArtists: $autoTrackArtists
    ) {
      id
      name
      url
      enabled
      autoTrackArtists
      lastSyncedAt
    }
  }
`;

export const UPDATE_PLAYLIST = gql`
  mutation UpdatePlaylist(
    $playlistId: Int!
    $name: String!
    $autoTrackArtists: Boolean!
  ) {
    updatePlaylist(
      playlistId: $playlistId
      name: $name
      autoTrackArtists: $autoTrackArtists
    ) {
      success
      message
    }
  }
`;
