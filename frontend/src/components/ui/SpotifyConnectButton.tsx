import { useMutation, useQuery } from '@apollo/client/react';
import { useState } from 'react';
import {
  GetSystemStatusDocument,
  DisconnectSpotifyDocument,
} from '../../types/generated/graphql';

export function SpotifyConnectButton() {
  const [isConnecting, setIsConnecting] = useState(false);
  const { data, loading, refetch } = useQuery(GetSystemStatusDocument);
  const [disconnectSpotify] = useMutation(DisconnectSpotifyDocument, {
    onCompleted: () => {
      refetch();
    },
  });

  const isConnected =
    data?.systemHealth.authentication.spotifyAuthMode === 'user-authenticated';

  const handleConnect = () => {
    setIsConnecting(true);
    // Open OAuth flow in a popup window
    const width = 600;
    const height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;

    const popup = window.open(
      '/auth/spotify/authorize',
      'spotify-oauth',
      `width=${width},height=${height},left=${left},top=${top}`
    );

    // Poll for popup closure (OAuth completion)
    const pollTimer = setInterval(() => {
      if (popup?.closed) {
        clearInterval(pollTimer);
        setIsConnecting(false);
        // Refresh to get updated status
        refetch();
      }
    }, 500);
  };

  const handleDisconnect = async () => {
    if (confirm('Are you sure you want to disconnect your Spotify account?')) {
      await disconnectSpotify();
    }
  };

  if (loading) {
    return (
      <button
        disabled
        className='px-4 py-2 text-sm font-medium text-gray-400 bg-gray-100 rounded-md cursor-not-allowed'
      >
        Loading...
      </button>
    );
  }

  if (isConnected) {
    return (
      <button
        onClick={handleDisconnect}
        className='px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors'
      >
        Disconnect
      </button>
    );
  }

  return (
    <button
      onClick={handleConnect}
      disabled={isConnecting}
      className='px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
    >
      {isConnecting ? 'Connecting...' : 'Connect Spotify'}
    </button>
  );
}
