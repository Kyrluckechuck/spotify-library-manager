import { createFileRoute, Link } from '@tanstack/react-router';
import React from 'react';

function Home() {
  return (
    <section className='space-y-6'>
      <div>
        <h1 className='text-2xl font-semibold mb-1'>Spotify Library Manager</h1>
        <p className='text-gray-700'>
          Quickly navigate and manage your library.
        </p>
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
