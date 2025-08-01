# Spotify Library Manager GraphQL API

This is the GraphQL API for the Spotify Library Manager. It provides a modern, type-safe interface for managing your Spotify library downloads.

## Features

- **Artists Management**
  - Track/untrack artists
  - Configure auto-download settings
  - Sync artist discographies

- **Albums Management**
  - View all albums
  - Mark albums as wanted/unwanted
  - Download albums

- **Playlists Management**
  - Track/untrack playlists
  - Configure auto-track settings for artists
  - Sync playlists

- **Download History**
  - View download history
  - Track download progress
  - Real-time updates via subscriptions

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python run.py
   ```

3. Visit the GraphQL Playground:
   ```
   http://localhost:5000/graphql
   ```

## Django Admin Interface

For database management and debugging, you can access the Django admin interface:

1. Start the admin server:
   ```bash
   make dev-admin
   ```

2. Visit the admin interface:
   ```
   http://localhost:8000/admin/
   ```

3. Login with your superuser credentials

The admin interface provides access to:
- **Artists** - View and manage tracked artists
- **Songs** - Browse downloaded songs and their metadata
- **Albums** - Manage album downloads and status
- **Download History** - Track download progress and history
- **Task History** - Monitor background task execution
- **Tracked Playlists** - Manage playlist tracking settings

> **Note**: The `make dev-admin` command automatically collects static files (CSS/JS) for the admin interface, so the styling should work correctly.

## Example Queries

### Get Tracked Artists
```graphql
query {
  artists(is_tracked: true) {
    edges {
      node {
        id
        name
        spotify_url
        image_url
        auto_download
        last_synced
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Track an Artist
```graphql
mutation {
  trackArtist(input: {
    artist_id: "spotify:artist:id",
    auto_download: true
  }) {
    id
    name
    is_tracked
    auto_download
  }
}
```

### Subscribe to Download Progress
```graphql
subscription {
  downloadProgress(entity_id: "album_id") {
    entity_id
    entity_type
    progress
    status
    message
  }
}
```

## Architecture

The API is built with:
- FastAPI - Web framework
- Strawberry - GraphQL library
- Uvicorn - ASGI server

It uses a cursor-based pagination system and follows GraphQL best practices for real-time updates via subscriptions. 
