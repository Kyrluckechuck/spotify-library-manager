import { createFileRoute } from '@tanstack/react-router';

function Playlists() {
  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Playlists</h1>
      <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
        Playlist list and management coming soon.
      </div>
    </section>
  );
}

export const Route = createFileRoute('/playlists')({
  component: Playlists,
}); 