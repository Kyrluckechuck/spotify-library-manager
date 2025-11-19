import { createFileRoute, Link } from '@tanstack/react-router';
import React from 'react';
import { useQuery } from '@apollo/client/react';
import { GetSystemStatusDocument } from '../types/generated/graphql';
import { SpotifyConnectButton } from '../components/ui/SpotifyConnectButton';

function Home() {
  const { data, loading } = useQuery(GetSystemStatusDocument, {
    pollInterval: 30 * 1000, // Poll every 30 seconds
  });

  return (
    <section className='space-y-6'>
      <div>
        <h1 className='text-2xl font-semibold mb-1'>Spotify Library Manager</h1>
        <p className='text-gray-700'>
          Quickly navigate and manage your library.
        </p>
      </div>

      {/* System Health Card */}
      <div className='bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-5'>
        <div className='flex items-start justify-between'>
          <div className='flex-1'>
            <div className='text-gray-900 font-semibold mb-3'>
              System Status
            </div>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
              {/* YouTube Music Authentication Status */}
              <div>
                <div className='text-xs text-gray-600 mb-1'>YouTube Music</div>
                {loading ? (
                  <div className='text-sm text-gray-500'>Loading...</div>
                ) : data?.systemHealth.authentication.cookiesValid ? (
                  <div className='flex items-center gap-2'>
                    <svg
                      className='h-4 w-4 text-green-500'
                      fill='currentColor'
                      viewBox='0 0 20 20'
                    >
                      <path
                        fillRule='evenodd'
                        d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
                        clipRule='evenodd'
                      />
                    </svg>
                    <span className='text-sm text-green-700 font-medium'>
                      Valid
                    </span>
                    {data.systemHealth.authentication.cookiesExpireInDays !==
                      null &&
                      data.systemHealth.authentication.cookiesExpireInDays <
                        30 && (
                        <span className='text-xs text-yellow-600'>
                          (
                          {data.systemHealth.authentication.cookiesExpireInDays}
                          d)
                        </span>
                      )}
                  </div>
                ) : (
                  <div className='flex items-center gap-2'>
                    <svg
                      className='h-4 w-4 text-red-500'
                      fill='currentColor'
                      viewBox='0 0 20 20'
                    >
                      <path
                        fillRule='evenodd'
                        d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293z'
                        clipRule='evenodd'
                      />
                    </svg>
                    <span className='text-sm text-red-700 font-medium'>
                      {data?.systemHealth.authentication.cookiesErrorType ||
                        'Invalid'}
                    </span>
                  </div>
                )}
              </div>

              {/* Spotify Authentication Mode */}
              <div>
                <div className='text-xs text-gray-600 mb-1'>Spotify Access</div>
                {loading ? (
                  <div className='text-sm text-gray-500'>Loading...</div>
                ) : data?.systemHealth.authentication.spotifyAuthMode ===
                  'user-authenticated' ? (
                  <div className='space-y-2'>
                    <div className='flex items-center gap-2'>
                      <svg
                        className='h-4 w-4 text-green-500'
                        fill='currentColor'
                        viewBox='0 0 20 20'
                      >
                        <path
                          fillRule='evenodd'
                          d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
                          clipRule='evenodd'
                        />
                      </svg>
                      <span className='text-sm text-green-700 font-medium'>
                        Private
                      </span>
                    </div>
                    <SpotifyConnectButton />
                  </div>
                ) : (
                  <div className='space-y-2'>
                    <div className='flex items-center gap-2'>
                      <svg
                        className='h-4 w-4 text-blue-500'
                        fill='currentColor'
                        viewBox='0 0 20 20'
                      >
                        <path
                          fillRule='evenodd'
                          d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z'
                          clipRule='evenodd'
                        />
                      </svg>
                      <span className='text-sm text-blue-700 font-medium'>
                        Public Only
                      </span>
                    </div>
                    <SpotifyConnectButton />
                  </div>
                )}
              </div>

              {/* Download Capability */}
              <div>
                <div className='text-xs text-gray-600 mb-1'>Downloads</div>
                {loading ? (
                  <div className='text-sm text-gray-500'>Loading...</div>
                ) : data?.systemHealth.canDownload ? (
                  <div className='flex items-center gap-2'>
                    <svg
                      className='h-4 w-4 text-green-500'
                      fill='currentColor'
                      viewBox='0 0 20 20'
                    >
                      <path
                        fillRule='evenodd'
                        d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
                        clipRule='evenodd'
                      />
                    </svg>
                    <span className='text-sm text-green-700 font-medium'>
                      Ready
                    </span>
                  </div>
                ) : (
                  <div className='flex items-center gap-2'>
                    <svg
                      className='h-4 w-4 text-red-500'
                      fill='currentColor'
                      viewBox='0 0 20 20'
                    >
                      <path
                        fillRule='evenodd'
                        d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293z'
                        clipRule='evenodd'
                      />
                    </svg>
                    <span className='text-sm text-red-700 font-medium'>
                      Blocked
                    </span>
                  </div>
                )}
              </div>

              {/* Queue Status */}
              <div>
                <div className='text-xs text-gray-600 mb-1'>Task Queue</div>
                {loading ? (
                  <div className='text-sm text-gray-500'>Loading...</div>
                ) : (
                  <div className='flex items-center gap-2'>
                    {data?.queueStatus.totalPendingTasks === 0 ? (
                      <>
                        <svg
                          className='h-4 w-4 text-gray-400'
                          fill='currentColor'
                          viewBox='0 0 20 20'
                        >
                          <path
                            fillRule='evenodd'
                            d='M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z'
                            clipRule='evenodd'
                          />
                        </svg>
                        <span className='text-sm text-gray-600'>Idle</span>
                      </>
                    ) : (
                      <>
                        <svg
                          className='h-4 w-4 text-blue-500 animate-spin'
                          fill='none'
                          viewBox='0 0 24 24'
                        >
                          <circle
                            className='opacity-25'
                            cx='12'
                            cy='12'
                            r='10'
                            stroke='currentColor'
                            strokeWidth='4'
                          />
                          <path
                            className='opacity-75'
                            fill='currentColor'
                            d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'
                          />
                        </svg>
                        <span className='text-sm text-blue-700 font-medium'>
                          {data?.queueStatus.totalPendingTasks} pending
                        </span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
          <Link
            to='/tasks'
            search={{}}
            className='ml-4 text-sm text-blue-600 hover:text-blue-700 font-medium'
          >
            View Tasks →
          </Link>
        </div>
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        <Link
          to='/artists'
          search={{}}
          className='block bg-white rounded-lg border border-gray-200 p-5 hover:shadow transition-shadow'
        >
          <div className='text-gray-900 font-semibold'>Artists</div>
          <div className='text-gray-600 text-sm'>Track and sync artists</div>
        </Link>

        <Link
          to='/albums'
          search={{ artistId: undefined }}
          className='block bg-white rounded-lg border border-gray-200 p-5 hover:shadow transition-shadow'
        >
          <div className='text-gray-900 font-semibold'>Albums</div>
          <div className='text-gray-600 text-sm'>Manage wanted/downloaded</div>
        </Link>

        <Link
          to='/songs'
          search={{ artistId: undefined, search: undefined }}
          className='block bg-white rounded-lg border border-gray-200 p-5 hover:shadow transition-shadow'
        >
          <div className='text-gray-900 font-semibold'>Songs</div>
          <div className='text-gray-600 text-sm'>View downloaded tracks</div>
        </Link>

        <Link
          to='/playlists'
          search={{}}
          className='block bg-white rounded-lg border border-gray-200 p-5 hover:shadow transition-shadow'
        >
          <div className='text-gray-900 font-semibold'>Playlists</div>
          <div className='text-gray-600 text-sm'>Manage and sync playlists</div>
        </Link>
      </div>

      <div className='bg-white rounded-lg border border-gray-200 p-5'>
        <div className='text-gray-900 font-semibold mb-2'>Get started</div>
        <ol className='list-decimal pl-5 space-y-1 text-sm text-gray-700'>
          <li>Visit Playlists to add or enable syncing</li>
          <li>Use Download URL to fetch a Spotify link</li>
          <li>Track artists you care about from Artists</li>
        </ol>
      </div>
    </section>
  );
}

export const Route = createFileRoute('/')({
  component: Home,
});
