import { createRootRoute, Outlet } from '@tanstack/react-router';
import { ToastProvider } from '../components/ui/ToastProvider';
import { Navbar } from '../components/Navbar';

function RootComponent() {
  return (
    <ToastProvider>
      <div className='min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50'>
        <Navbar />
        <main className='max-w-7xl mx-auto px-6 py-10'>
          <div className='bg-white/90 rounded-xl shadow-lg p-8 min-h-[400px]'>
            <Outlet />
          </div>
        </main>
      </div>
    </ToastProvider>
  );
}

export const Route = createRootRoute({
  component: RootComponent,
});
