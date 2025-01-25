# Migration to Spotdl
## Remaining Work
- Get 320kbps working [(requires upstream fix)](https://github.com/spotDL/spotify-downloader/issues/2279)
- Add migration to Artist table to add `uri`, add helper to auto-fix with gid_to_uri; this is the value stored in spotdl outputs
- Implement spotdl.py, re-implementing the behaviour of spotify_aac_downloader:
  - Individual songs need to be tracked, marked as successful
  - Individual albums need to be tracked, marked as successful (unsure how in this flow)
  - Individual artists need to be tracked, added
  - Playlists need to be tracked
  - 