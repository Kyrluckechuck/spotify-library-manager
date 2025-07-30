import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ArtistContext } from '../ArtistContext';

describe('ArtistContext', () => {
  it('renders artist name and songs count', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    expect(screen.getByText('Test Artist')).toBeInTheDocument();
    expect(screen.getByText('42 songs')).toBeInTheDocument();
  });

  it('renders artist name and albums count', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='albums'
        totalCount={15}
      />
    );

    expect(screen.getByText('Test Artist')).toBeInTheDocument();
    expect(screen.getByText('15 albums')).toBeInTheDocument();
  });

  it('renders back to artists link', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    expect(screen.getByText('← Back to Artists')).toBeInTheDocument();
  });

  it('renders view albums link when content type is songs', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    expect(screen.getByText('View Albums')).toBeInTheDocument();
  });

  it('renders view songs link when content type is albums', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='albums'
        totalCount={15}
      />
    );

    expect(screen.getByText('View Songs')).toBeInTheDocument();
  });

  it('has correct styling classes', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    // Find the main container div by looking for the gradient class
    const container = screen.getByText('Test Artist').closest('div')
      ?.parentElement?.parentElement;
    expect(container).toHaveClass(
      'bg-gradient-to-r',
      'from-indigo-50',
      'to-purple-50',
      'border',
      'border-indigo-200',
      'rounded-lg',
      'p-4',
      'mb-6'
    );
  });

  it('displays artist name with correct styling', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    const artistName = screen.getByText('Test Artist');
    expect(artistName).toHaveClass(
      'text-lg',
      'font-semibold',
      'text-indigo-900'
    );
  });

  it('displays count with correct styling', () => {
    render(
      <ArtistContext
        artistId={123}
        artistName='Test Artist'
        contentType='songs'
        totalCount={42}
      />
    );

    const count = screen.getByText('42 songs');
    expect(count).toHaveClass('text-sm', 'text-indigo-700');
  });
});
