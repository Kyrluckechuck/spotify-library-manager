import { useQuery } from '@apollo/client/react';
import { GetSystemHealthDocument } from '../../types/generated/graphql';

export function AuthStatusBanner() {
  const { data, loading } = useQuery(GetSystemHealthDocument, {
    // Poll every 5 minutes to detect cookie expiration
    pollInterval: 5 * 60 * 1000,
  });

  // Don't show anything while loading
  if (loading || !data?.systemHealth) {
    return null;
  }

  const { canDownload, downloadBlockerReason, authentication } =
    data.systemHealth;

  // Show error banner if downloads are blocked
  if (!canDownload) {
    const errorType = authentication.cookiesErrorType;
    const errorMessage =
      authentication.cookiesErrorMessage || downloadBlockerReason;

    const bgColor = 'bg-red-50';
    const borderColor = 'border-red-400';
    const textColor = 'text-red-800';
    const iconColor = 'text-red-400';
    let title = 'Authentication Error';

    if (errorType === 'expired') {
      title = 'Cookies Expired';
    } else if (errorType === 'malformed') {
      title = 'Invalid Cookie Format';
    } else if (errorType === 'missing') {
      title = 'Cookies Not Found';
    }

    return (
      <div
        className={`border-l-4 ${borderColor} ${bgColor} p-4 mb-4`}
        role='alert'
      >
        <div className='flex items-start'>
          <div className='flex-shrink-0'>
            <svg
              className={`h-5 w-5 ${iconColor}`}
              xmlns='http://www.w3.org/2000/svg'
              viewBox='0 0 20 20'
              fill='currentColor'
              aria-hidden='true'
            >
              <path
                fillRule='evenodd'
                d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z'
                clipRule='evenodd'
              />
            </svg>
          </div>
          <div className='ml-3 flex-1'>
            <h3 className={`text-sm font-medium ${textColor}`}>{title}</h3>
            <div className={`mt-2 text-sm ${textColor}`}>
              <p>{errorMessage}</p>
              <p className='mt-2'>
                <strong>How to fix:</strong>
              </p>
              <ol className='list-decimal list-inside mt-1 space-y-1'>
                <li>
                  Export cookies from YouTube Music using a browser extension
                  (like &ldquo;Get youtube_music_cookies.txt LOCALLY&rdquo;)
                </li>
                <li>
                  Save the cookies in Netscape format to{' '}
                  <code className='bg-red-100 px-1 py-0.5 rounded'>
                    /config/youtube_music_cookies.txt
                  </code>
                </li>
                <li>Restart the application</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show warning if cookies expire soon (within 7 days)
  if (
    authentication.cookiesExpireInDays !== null &&
    authentication.cookiesExpireInDays !== undefined &&
    authentication.cookiesExpireInDays < 7
  ) {
    return (
      <div
        className='border-l-4 border-yellow-400 bg-yellow-50 p-4 mb-4'
        role='alert'
      >
        <div className='flex items-start'>
          <div className='flex-shrink-0'>
            <svg
              className='h-5 w-5 text-yellow-400'
              xmlns='http://www.w3.org/2000/svg'
              viewBox='0 0 20 20'
              fill='currentColor'
              aria-hidden='true'
            >
              <path
                fillRule='evenodd'
                d='M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z'
                clipRule='evenodd'
              />
            </svg>
          </div>
          <div className='ml-3'>
            <h3 className='text-sm font-medium text-yellow-800'>
              Cookies Expiring Soon
            </h3>
            <div className='mt-2 text-sm text-yellow-700'>
              <p>
                Your YouTube Music cookies will expire in{' '}
                <strong>{authentication.cookiesExpireInDays} day(s)</strong>.
                Consider re-exporting them soon to avoid interruptions.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No warnings needed
  return null;
}
