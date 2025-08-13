import React, { useCallback, useMemo, useState } from 'react';
import { ToastContext } from './ToastContext';
import type { Toast, ToastContextValue, ToastType } from './ToastContext';

function makeId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const add = useCallback(
    (message: string, type: ToastType = 'info') => {
      const id = makeId();
      setToasts(prev => [...prev, { id, message, type }]);
      // Auto-dismiss after 2.2s
      window.setTimeout(() => remove(id), 2200);
    },
    [remove]
  );

  const value = useMemo<ToastContextValue>(
    () => ({
      add,
      success: (m: string) => add(m, 'success'),
      error: (m: string) => add(m, 'error'),
      info: (m: string) => add(m, 'info'),
    }),
    [add]
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className='fixed top-4 right-4 z-50 space-y-2'>
        {toasts.map(t => (
          <div
            key={t.id}
            className={
              `flex items-center gap-2 px-4 py-2 rounded shadow text-sm ` +
              (t.type === 'success'
                ? 'bg-green-100 text-green-800 border border-green-200'
                : t.type === 'error'
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : 'bg-gray-100 text-gray-800 border border-gray-200')
            }
            role='status'
            aria-live='polite'
          >
            {t.type === 'success' && (
              <span className='w-3 h-3 rounded-full bg-green-600 inline-block' />
            )}
            {t.type === 'error' && (
              <span className='w-3 h-3 rounded-full bg-red-600 inline-block' />
            )}
            {t.type === 'info' && (
              <span className='w-3 h-3 rounded-full bg-gray-600 inline-block' />
            )}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
// hook is exported from useToast.ts to satisfy react-refresh rule
