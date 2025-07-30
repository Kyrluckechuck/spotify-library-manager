import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SortableTableHeader } from '../SortableTableHeader';

describe('SortableTableHeader', () => {
  const mockOnSort = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with children', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    expect(screen.getByText(/Name/)).toBeInTheDocument();
  });

  it('shows ascending arrow when sorted ascending', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    expect(screen.getByText(/↑/)).toBeInTheDocument();
  });

  it('shows descending arrow when sorted descending', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='desc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    expect(screen.getByText(/↓/)).toBeInTheDocument();
  });

  it('shows both arrows when not sorted', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='other'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    expect(screen.getByText(/↕️/)).toBeInTheDocument();
  });

  it('calls onSort when clicked', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='other'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).toBeInTheDocument();
    if (header) {
      fireEvent.click(header);
    }

    expect(mockOnSort).toHaveBeenCalledWith('name');
  });

  it('does not call onSort when field is null', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field={null}
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).toBeInTheDocument();
    if (header) {
      fireEvent.click(header);
    }

    expect(mockOnSort).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
              className='custom-class'
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).toHaveClass('custom-class');
  });

  it('has correct base styling classes', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).toHaveClass(
      'px-6',
      'py-3',
      'text-left',
      'text-xs',
      'font-medium',
      'text-gray-500',
      'uppercase',
      'tracking-wider'
    );
  });

  it('has interactive styling when field is provided', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field='name'
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).toHaveClass('cursor-pointer', 'hover:bg-gray-100');
  });

  it('does not have interactive styling when field is null', () => {
    render(
      <table>
        <thead>
          <tr>
            <SortableTableHeader
              field={null}
              currentSortField='name'
              currentSortDirection='asc'
              onSort={mockOnSort}
            >
              Name
            </SortableTableHeader>
          </tr>
        </thead>
      </table>
    );

    const header = screen.getByText(/Name/).closest('th');
    expect(header).not.toHaveClass('cursor-pointer', 'hover:bg-gray-100');
  });
});
