import { createFileRoute } from '@tanstack/react-router';

function Home() {
  return (
    <section>
      <h1 className='text-2xl font-semibold mb-4'>Home</h1>
      <p className='text-gray-700'>
        Welcome to your Spotify Library Manager. Manage your music with ease.
      </p>
    </section>
  );
}

export const Route = createFileRoute('/')({
  component: Home,
});
