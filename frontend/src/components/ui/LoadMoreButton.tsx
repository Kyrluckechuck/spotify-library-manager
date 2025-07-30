interface LoadMoreButtonProps {
  hasNextPage: boolean;
  loading: boolean;
  remainingCount: number;
  onLoadMore: () => void;
}

export function LoadMoreButton({
  hasNextPage,
  loading,
  remainingCount,
  onLoadMore,
}: LoadMoreButtonProps) {
  if (!hasNextPage) {
    return null;
  }

  return (
    <div className='p-4 text-center border-t border-gray-200'>
      <button
        onClick={onLoadMore}
        disabled={loading}
        className='px-6 py-3 rounded font-medium transition-colors'
        style={{
          backgroundColor: loading ? '#6b7280' : '#3730a3',
          color: 'white',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Loading...' : `Load More (${remainingCount} remaining)`}
      </button>
    </div>
  );
}
