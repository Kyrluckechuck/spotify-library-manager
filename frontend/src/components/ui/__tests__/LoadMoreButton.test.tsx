import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { LoadMoreButton } from '../LoadMoreButton';

describe('LoadMoreButton', () => {
  const mockOnLoadMore = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders button when hasNextPage is true', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={false}
        remainingCount={10}
        onLoadMore={mockOnLoadMore}
      />
    );

    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Load More (10 remaining)')).toBeInTheDocument();
  });

  it('does not render when hasNextPage is false', () => {
    render(
      <LoadMoreButton
        hasNextPage={false}
        loading={false}
        remainingCount={10}
        onLoadMore={mockOnLoadMore}
      />
    );

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('shows loading state when loading is true', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={true}
        remainingCount={5}
        onLoadMore={mockOnLoadMore}
      />
    );

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('calls onLoadMore when clicked and not loading', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={false}
        remainingCount={15}
        onLoadMore={mockOnLoadMore}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnLoadMore).toHaveBeenCalledTimes(1);
  });

  it('does not call onLoadMore when clicked while loading', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={true}
        remainingCount={15}
        onLoadMore={mockOnLoadMore}
      />
    );

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(mockOnLoadMore).not.toHaveBeenCalled();
  });

  it('displays correct remaining count', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={false}
        remainingCount={42}
        onLoadMore={mockOnLoadMore}
      />
    );

    expect(screen.getByText('Load More (42 remaining)')).toBeInTheDocument();
  });

  it('has correct styling classes', () => {
    render(
      <LoadMoreButton
        hasNextPage={true}
        loading={false}
        remainingCount={10}
        onLoadMore={mockOnLoadMore}
      />
    );

    const container = screen.getByRole('button').parentElement;
    expect(container).toHaveClass(
      'p-4',
      'text-center',
      'border-t',
      'border-gray-200'
    );
  });
});
