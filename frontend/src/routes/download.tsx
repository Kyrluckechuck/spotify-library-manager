import React, { useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { DownloadUrlModal } from '../components/ui/DownloadUrlModal';

function DownloadPage() {
  const [open, setOpen] = useState(false);
  return (
    <section className='space-y-6'>
      <div>
        <h1 className='text-2xl font-semibold mb-1'>Download URL</h1>
        <p className='text-gray-700'>Paste a Spotify URL or URI to download.</p>
      </div>
      <div className='bg-white rounded-lg border border-gray-200 p-5'>
        <button
          onClick={() => setOpen(true)}
          className='px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors'
        >
          Open Download Dialog
        </button>
      </div>
      <DownloadUrlModal
        isOpen={open}
        onClose={() => setOpen(false)}
        onSuccess={() => setOpen(false)}
      />
    </section>
  );
}

export const Route = createFileRoute('/download')({
  component: DownloadPage,
});
