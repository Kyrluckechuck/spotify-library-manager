import type { ContentType } from '../types/shared';

export interface DetectedContent {
  type: ContentType;
  icon: string;
  label: string;
  buttonText: string;
}

/**
 * Detects the type of Spotify content from a URL
 * @param url - Spotify URL to analyze
 * @returns Detected content information including type, icon, and labels
 */
export function detectSpotifyContentType(url: string): DetectedContent {
  const trimmedUrl = url.trim().toLowerCase();

  if (!trimmedUrl) {
    return {
      type: 'unknown',
      icon: '💡',
      label: 'Enter a Spotify URL to detect content type',
      buttonText: 'Download',
    };
  }

  // Check for playlist
  if (trimmedUrl.includes('/playlist/') || trimmedUrl.includes('playlist:')) {
    return {
      type: 'playlist',
      icon: '📜',
      label: 'Playlist detected',
      buttonText: 'Download Playlist',
    };
  }

  // Check for artist
  if (trimmedUrl.includes('/artist/') || trimmedUrl.includes('artist:')) {
    return {
      type: 'artist',
      icon: '🎤',
      label: 'Artist detected',
      buttonText: 'Download Artist',
    };
  }

  // Check for album
  if (trimmedUrl.includes('/album/') || trimmedUrl.includes('album:')) {
    return {
      type: 'album',
      icon: '💿',
      label: 'Album detected',
      buttonText: 'Download Album',
    };
  }

  // Check for track/song
  if (trimmedUrl.includes('/track/') || trimmedUrl.includes('track:')) {
    return {
      type: 'track',
      icon: '🎵',
      label: 'Track detected',
      buttonText: 'Download Track',
    };
  }

  // If URL contains spotify but not recognized
  if (trimmedUrl.includes('spotify')) {
    return {
      type: 'unknown',
      icon: '❌',
      label: 'URL not recognized - please check format',
      buttonText: 'Download',
    };
  }

  // Generic URL
  return {
    type: 'unknown',
    icon: '❓',
    label: 'Unknown URL format',
    buttonText: 'Download',
  };
}

/**
 * Extracts a playlist name from a Spotify URL
 * @param url - Spotify playlist URL
 * @returns Extracted or default playlist name
 */
export function extractPlaylistName(url: string): string {
  // Try to extract a reasonable name from the URL
  const match = url.match(/playlist\/([a-zA-Z0-9]+)/);
  if (match) {
    return `Playlist ${match[1]}`;
  }
  return 'Downloaded Playlist';
}
