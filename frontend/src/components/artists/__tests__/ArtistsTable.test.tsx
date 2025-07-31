import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ArtistsTable } from '../ArtistsTable';
import type { Artist } from '../../../types/generated/graphql';

describe('ArtistsTable', () => {
  const mockArtists: Artist[] = [
    {
      id: 1,
      gid: 'artist1',
      name: 'Artist 1',
      isTracked: true,
      lastSynced: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      gid: 'artist2',
      name: 'Artist 2',
      isTracked: false,
      lastSynced: null,
    },
  ];

  const mockOnTrackToggle = vi.fn();
  const mockOnSyncArtist = vi.fn();
  const mockOnSort = vi.fn();

  it('renders artists in table', () => {
    render(
      <ArtistsTable
        artists={mockArtists}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={false}
      />
    );

    expect(screen.getByText('Artist 1')).toBeInTheDocument();
    expect(screen.getByText('Artist 2')).toBeInTheDocument();
  });

  it('shows tracked status correctly', () => {
    render(
      <ArtistsTable
        artists={mockArtists}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={false}
      />
    );

    // Check for tracked indicators
    expect(screen.getByText('Tracked')).toBeInTheDocument();
    expect(screen.getByText('Not Tracked')).toBeInTheDocument();
  });

  it('calls onTrackToggle when track button is clicked', () => {
    render(
      <ArtistsTable
        artists={mockArtists}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={false}
      />
    );

    const trackButtons = screen.getAllByRole('button', { name: /track/i });
    fireEvent.click(trackButtons[0]);

    expect(mockOnTrackToggle).toHaveBeenCalledWith(mockArtists[0]);
  });

  it('calls onSyncArtist when sync button is clicked', () => {
    render(
      <ArtistsTable
        artists={mockArtists}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={false}
      />
    );

    const syncButtons = screen.getAllByRole('button', { name: /sync/i });
    fireEvent.click(syncButtons[0]);

    expect(mockOnSyncArtist).toHaveBeenCalledWith(1);
  });

  it('shows loading state', () => {
    render(
      <ArtistsTable
        artists={[]}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={true}
      />
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows empty state when no artists', () => {
    render(
      <ArtistsTable
        artists={[]}
        sortField={null}
        sortDirection='asc'
        onSort={mockOnSort}
        onTrackToggle={mockOnTrackToggle}
        onSyncArtist={mockOnSyncArtist}
        loading={false}
      />
    );

    expect(screen.getByText(/no artists found/i)).toBeInTheDocument();
  });
});
