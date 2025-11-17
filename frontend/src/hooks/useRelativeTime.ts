import { useState, useEffect } from 'react';

/**
 * Hook that returns a human-readable relative time string that updates every 5 seconds
 * @param date - The date to calculate relative time from
 * @returns A string like "just now", "5 minutes ago", "2 hours ago"
 */
export function useRelativeTime(date: Date): string {
  const [relativeTime, setRelativeTime] = useState('');

  useEffect(() => {
    const updateRelativeTime = () => {
      const now = new Date();
      const secondsAgo = Math.floor((now.getTime() - date.getTime()) / 1000);

      if (secondsAgo < 10) {
        setRelativeTime('just now');
      } else if (secondsAgo < 45) {
        setRelativeTime('30 seconds ago');
      } else if (secondsAgo < 90) {
        setRelativeTime('a minute ago');
      } else if (secondsAgo < 300) {
        setRelativeTime('a few minutes ago');
      } else if (secondsAgo < 600) {
        setRelativeTime('5 minutes ago');
      } else if (secondsAgo < 1800) {
        setRelativeTime('10 minutes ago');
      } else if (secondsAgo < 3600) {
        setRelativeTime('30 minutes ago');
      } else if (secondsAgo < 7200) {
        setRelativeTime('an hour ago');
      } else {
        const hours = Math.floor(secondsAgo / 3600);
        setRelativeTime(`${hours} hours ago`);
      }
    };

    updateRelativeTime();
    // Update every 5 seconds instead of every second
    const interval = setInterval(updateRelativeTime, 5000);

    return () => clearInterval(interval);
  }, [date]);

  return relativeTime;
}
