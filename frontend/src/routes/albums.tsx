import { createFileRoute } from '@tanstack/react-router';

function Albums() {
  return (
    <section>
      <h1 className="text-2xl font-semibold mb-4">Albums</h1>
      <div className="bg-white rounded shadow p-6 min-h-[200px] flex items-center justify-center text-gray-400">
        Album list and management coming soon.
      </div>
    </section>
  );
}

export const Route = createFileRoute('/albums')({
  component: Albums,
}); 