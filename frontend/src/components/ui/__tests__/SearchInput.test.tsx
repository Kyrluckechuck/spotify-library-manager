import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SearchInput } from '../SearchInput';

describe('SearchInput', () => {
  it('renders with placeholder text', () => {
    const mockOnSearch = vi.fn();
    render(
      <SearchInput onSearch={mockOnSearch} placeholder='Search artists...' />
    );

    expect(
      screen.getByPlaceholderText('Search artists...')
    ).toBeInTheDocument();
  });

  it('calls onSearch when user types', async () => {
    const mockOnSearch = vi.fn();
    render(
      <SearchInput
        onSearch={mockOnSearch}
        placeholder='Search...'
        debounceMs={100}
      />
    );

    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'test query' } });

    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 150));

    expect(mockOnSearch).toHaveBeenCalledWith('test query');
  });

  it('debounces search calls', async () => {
    const mockOnSearch = vi.fn();
    render(
      <SearchInput
        onSearch={mockOnSearch}
        placeholder='Search...'
        debounceMs={100}
      />
    );

    const input = screen.getByPlaceholderText('Search...');

    // Type multiple characters quickly
    fireEvent.change(input, { target: { value: 't' } });
    fireEvent.change(input, { target: { value: 'te' } });
    fireEvent.change(input, { target: { value: 'tes' } });
    fireEvent.change(input, { target: { value: 'test' } });

    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 150));

    // Should only call once with final value
    expect(mockOnSearch).toHaveBeenCalledTimes(1);
    expect(mockOnSearch).toHaveBeenCalledWith('test');
  });

  it('clears search when clear button is clicked', () => {
    const mockOnSearch = vi.fn();
    render(<SearchInput onSearch={mockOnSearch} placeholder='Search...' />);

    const input = screen.getByPlaceholderText('Search...');
    fireEvent.change(input, { target: { value: 'test' } });

    // Clear button should appear
    const clearButton = screen.getByRole('button');
    fireEvent.click(clearButton);

    expect(input).toHaveValue('');
  });
});
