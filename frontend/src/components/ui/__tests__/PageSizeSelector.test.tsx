import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PageSizeSelector } from '../PageSizeSelector';

describe('PageSizeSelector', () => {
  const mockOnPageSizeChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with default options', () => {
    render(
      <PageSizeSelector pageSize={50} onPageSizeChange={mockOnPageSizeChange} />
    );

    expect(screen.getByLabelText('Show:')).toBeInTheDocument();
    expect(screen.getByDisplayValue('50')).toBeInTheDocument();
  });

  it('renders with custom options', () => {
    const customOptions = [10, 25, 50, 75];
    render(
      <PageSizeSelector
        pageSize={25}
        onPageSizeChange={mockOnPageSizeChange}
        options={customOptions}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();

    // Check that all options are rendered
    customOptions.forEach(option => {
      expect(screen.getByText(option.toString())).toBeInTheDocument();
    });
  });

  it('calls onPageSizeChange when selection changes', () => {
    render(
      <PageSizeSelector pageSize={50} onPageSizeChange={mockOnPageSizeChange} />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '100' } });

    expect(mockOnPageSizeChange).toHaveBeenCalledWith(100);
  });

  it('displays current page size as selected', () => {
    render(
      <PageSizeSelector
        pageSize={200}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByDisplayValue('200')).toBeInTheDocument();
  });

  it('has correct styling classes', () => {
    render(
      <PageSizeSelector pageSize={50} onPageSizeChange={mockOnPageSizeChange} />
    );

    const container = screen.getByLabelText('Show:').parentElement;
    expect(container).toHaveClass('flex', 'items-center', 'gap-2');
  });

  it('has proper accessibility attributes', () => {
    render(
      <PageSizeSelector pageSize={50} onPageSizeChange={mockOnPageSizeChange} />
    );

    const select = screen.getByRole('combobox');
    const label = screen.getByText('Show:');

    expect(select).toHaveAttribute('id', 'pageSize');
    expect(label).toHaveAttribute('for', 'pageSize');
  });

  it('handles numeric conversion correctly', () => {
    render(
      <PageSizeSelector pageSize={50} onPageSizeChange={mockOnPageSizeChange} />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '200' } });

    expect(mockOnPageSizeChange).toHaveBeenCalledWith(200);
    expect(typeof mockOnPageSizeChange.mock.calls[0][0]).toBe('number');
  });
});
