import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Navbar } from '../Navbar';
import { DownloadModalProvider } from '../ui/DownloadModalProvider';
import { ToastProvider } from '../ui/ToastProvider';

const renderNavbar = () => {
  return render(
    <ToastProvider>
      <DownloadModalProvider>
        <Navbar />
      </DownloadModalProvider>
    </ToastProvider>
  );
};

describe('Navbar', () => {
  it('renders the application title', () => {
    renderNavbar();

    expect(screen.getByText('Spotify Library Manager')).toBeInTheDocument();
  });

  it('renders all navigation links and download button', () => {
    renderNavbar();

    const expectedLinks = ['Home', 'Artists', 'Albums', 'Playlists', 'Tasks'];

    expectedLinks.forEach(linkText => {
      expect(screen.getByText(linkText)).toBeInTheDocument();
    });

    // Download is now a button, not a link
    expect(screen.getByText('Download')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /download/i })
    ).toBeInTheDocument();
  });

  it('has proper navigation structure', () => {
    renderNavbar();

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();

    // Check that nav links are anchor elements (5 links + 1 title link)
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(6); // Title + 5 nav links (Home, Artists, Albums, Playlists, Tasks)

    // Check that download button exists
    const downloadButton = screen.getByRole('button', { name: /download/i });
    expect(downloadButton).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    renderNavbar();

    const navbar = screen.getByRole('navigation');
    expect(navbar).toHaveClass('bg-white', 'border-b', 'border-gray-300');

    const title = screen.getByText('Spotify Library Manager');
    expect(title).toHaveClass('font-extrabold', 'text-2xl');
  });
});
