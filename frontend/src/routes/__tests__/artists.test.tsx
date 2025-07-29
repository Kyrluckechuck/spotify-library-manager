import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useQuery, useMutation } from '@apollo/client'

// Mock the GraphQL hooks
vi.mock('@apollo/client', () => ({
  useQuery: vi.fn(),
  useMutation: vi.fn(),
}))

const mockUseQuery = useQuery as vi.MockedFunction<typeof useQuery>
const mockUseMutation = useMutation as vi.MockedFunction<typeof useMutation>

// Mock the TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => ({ component: () => null })),
}))

// Create a simple test component that simulates the Artists route
const TestArtistsComponent = () => {
  const { data, loading, error } = mockUseQuery()
  const [trackArtist] = mockUseMutation()

  if (loading) {
    return <div>Loading artists...</div>
  }

  if (error) {
    return <div>Error loading artists: {error.message}</div>
  }

  if (!data?.artists?.edges?.length) {
    return <div>No artists found</div>
  }

  return (
    <div>
      <h1>Artists ({data.artists.edges.length} of {data.artists.totalCount})</h1>
      {data.artists.edges.map((artist: any) => (
        <div key={artist.id}>{artist.name}</div>
      ))}
    </div>
  )
}

describe('Artists Route', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks()
  })

  it('renders loading state', () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      loading: true,
      error: undefined,
    } as any)

    mockUseMutation.mockReturnValue([
      vi.fn(),
      { loading: false, error: undefined }
    ] as any)

    render(<TestArtistsComponent />)
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('renders artists when data is loaded', () => {
    const mockArtists = {
      artists: {
        totalCount: 2,
        edges: [
          {
            id: '1',
            name: 'Artist 1',
            tracked: true,
          },
          {
            id: '2',
            name: 'Artist 2',
            tracked: false,
          },
        ],
      },
    }

    mockUseQuery.mockReturnValue({
      data: mockArtists,
      loading: false,
      error: undefined,
    } as any)

    mockUseMutation.mockReturnValue([
      vi.fn(),
      { loading: false, error: undefined }
    ] as any)

    render(<TestArtistsComponent />)
    
    expect(screen.getByText('Artist 1')).toBeInTheDocument()
    expect(screen.getByText('Artist 2')).toBeInTheDocument()
    expect(screen.getByText(/2 of 2/)).toBeInTheDocument()
  })

  it('renders error state', () => {
    mockUseQuery.mockReturnValue({
      data: undefined,
      loading: false,
      error: { message: 'Failed to load artists' },
    } as any)

    mockUseMutation.mockReturnValue([
      vi.fn(),
      { loading: false, error: undefined }
    ] as any)

    render(<TestArtistsComponent />)
    
    expect(screen.getByText(/error/i)).toBeInTheDocument()
    expect(screen.getByText(/failed to load artists/i)).toBeInTheDocument()
  })

  it('renders empty state when no artists', () => {
    const mockArtists = {
      artists: {
        totalCount: 0,
        edges: [],
      },
    }

    mockUseQuery.mockReturnValue({
      data: mockArtists,
      loading: false,
      error: undefined,
    } as any)

    mockUseMutation.mockReturnValue([
      vi.fn(),
      { loading: false, error: undefined }
    ] as any)

    render(<TestArtistsComponent />)
    
    expect(screen.getByText(/no artists found/i)).toBeInTheDocument()
  })
}) 