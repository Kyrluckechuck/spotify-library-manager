import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { PageHeader } from '../PageHeader';

describe('PageHeader', () => {
  it('renders title', () => {
    render(<PageHeader title='Test Page' />);

    expect(screen.getByText('Test Page')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<PageHeader title='Test Page' subtitle='This is a test page' />);

    expect(screen.getByText('This is a test page')).toBeInTheDocument();
  });

  it('renders children when provided', () => {
    render(
      <PageHeader title='Test Page'>
        <button>Test Button</button>
      </PageHeader>
    );

    expect(screen.getByText('Test Button')).toBeInTheDocument();
  });

  it('has correct default styling', () => {
    render(<PageHeader title='Test Page' />);

    const title = screen.getByText('Test Page');
    expect(title).toHaveClass('text-3xl', 'font-bold', 'text-gray-900');
  });
});
