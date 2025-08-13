import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Navbar } from '../Navbar';

describe('Navbar', () => {
  it('renders the application title', () => {
    render(<Navbar />);

    expect(screen.getByText('Spotify Library Manager')).toBeInTheDocument();
  });

  it('renders all navigation links', () => {
    render(<Navbar />);

    const expectedLinks = [
      'Home',
      'Artists',
      'Albums',
      'Playlists',
      'Tasks',
      'Download',
    ];

    expectedLinks.forEach(linkText => {
      expect(screen.getByText(linkText)).toBeInTheDocument();
    });
  });

  it('has proper navigation structure', () => {
    render(<Navbar />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();

    // Check that all links are anchor elements (mocked as <a> tags)
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(7); // Title + 6 nav links (Home, Artists, Albums, Playlists, Tasks, Download)
  });

  it('applies correct CSS classes', () => {
    render(<Navbar />);

    const navbar = screen.getByRole('navigation');
    expect(navbar).toHaveClass('bg-white', 'border-b', 'border-gray-300');

    const title = screen.getByText('Spotify Library Manager');
    expect(title).toHaveClass('font-extrabold', 'text-2xl');
  });
});
