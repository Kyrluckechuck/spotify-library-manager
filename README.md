# Spotify Library Manager
Originally derived as a fork of [glomatico/spotify-aac-downloader](https://github.com/glomatico/spotify-aac-downloader), this has grown into a completely different behemoth.

This started as a simple want to mass-download songs for specific artists since they were not otherwise available, and snowballed into a full-fledged library management platform including:
- Task queuing system, allowing downloads to continue after restarts*
  - *Semi-lossy, where jobs which are interrupted will not be recovered, but any un-started jobs will be. Jobs can safely be restarted manually, though.
- Artist discography syncing and mass-downloading
- Artist tracking - auto downloading missing releases (including new)
- Fetch metadata for all albums available for tracked artists
- Mark un-downloaded albums as non-wanted
  - Useful for artists which have a large backlog of music you don't want, but you still want to track their latest stuff automatically
- Download all "wanted" albums (via queued tasks)
- Download playlists/albums directly
  - Can choose to auto mark all artists on given playlists as "Tracked", useful for "favourites" playlists
- Tracked playlist syncing
 - Can continuously refresh and sync (every 4 hours)
 - Can include auto-tracking new artists (such as tracking a "favourites" playlist)
- Artist tracking supporting auto-downloading newly released albums (including tracks)
 - Can continuously refresh and sync (every 6 hours)
 - Will download missing releases (every 6 hours, offset by 45 minutes)

Features from spotify-aac-downloader:
* Download songs in 128kbps AAC or 256kbps AAC with a premium account
* Download synced lyrics
* Includes a device wvd so no need to load your own!
     
## Notes
While this has a lot of opportunity to improve, it's reached a "stable" state for my personal usage. Therefore I will fix critical issues as I encounter them, but will not actively be working on additional features except when inspiration hits me, or there are specific community requests.

If there is enough desire from folks, I am happy to put more time in, and of course always welcome Pull Requests!

## TODO
### Features To Add:
- [ ] Fallback to yt-dlp when no Spotify AAC
- [X] Tracked Playlists
  - [ ] Improve update experience (not URL-locked)
- [ ] Allow periodic tasks to be configurable intervals
- [ ] Add artists directly (by artist name?)

### Other Changes:
- [ ] Re-add Downloader configuration(s) loading via `settings.yaml`
- [ ] Improve onboarding documentation
  - [ ] Add critical steps such as first startup, any missing examples, etc

## Screenshots
![Main Dashboard](https://github.com/Kyrluckechuck/spotify-library-manager/assets/7606153/6d32f8d5-fe6b-4884-a5a9-7970aaba284a)
![Example Artist Page](https://github.com/Kyrluckechuck/spotify-library-manager/assets/7606153/2dcceee2-41e4-4101-b257-2ca754017c20)



## Configuration / Usage
It's currently being designed to mostly run on Linux-based systems, however, many of the configurations should only require minor tweaks to adjust for Windows-based systems.

Existing settings (that are applicable) are now set via `/config/settings.yaml`, and will override any default configurations.
They must follow the format:
```yaml
default:
    final_path: "/mnt/music_spotify"
```

## Running From Docker (recommended)
An example docker-compose file is included in this repo that can be dropped into Portainer or your flavour of running it, swapping out any mounts for your local directory structure

1. Export your cookies using this Google Chrome extension on the Spotify website: https://chrome.google.com/webstore/detail/open-cookiestxt/gdocmgbfkjnnpapoeobnolbbkoibbcif
   - Make sure to be logged in
   - Save it as `cookies.txt`
2. // TODO - Execute docker container, mapping /config to the local directory with your cookies.txt, device.wvd, and settings.yml

## Running From Source (not recommended unless developing)
> [!WARNING]
> While this is not recommended unless you are developing, this _should_ work just fine.

> [!NOTE]
> This is currently only configured for running on Unix-based systems due to the default configuration folder, but if anyone wants to update this doc with the correct configuration I'd welcome the upload!
>
> If developing on Windows, using WSL should work just fine, installing python via `apt`

1. Install Python 3.10 or higher
2. Place your cookies in `/config/` as `cookies.txt`
    * You can export your cookies by using this Google Chrome extension on Spotify website: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc. Make sure to be logged in.


5. (Optional) I personally like setting huey into instant-run mode so as to not have a separate worker, but if you are using this for non-development I would advise against this due to degraded performance!
This should be placed in `/config/` as `settings.yaml`
```yaml
default:
  final_path: "/mnt/h/music_spotify"
  HUEY: {
    immediate: true,
    immediate_use_memory: true,
  }
```
7. Execute it using
```bash
bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:5000"
```

## Configuration (IGNORE, Half-updated and docker is the intended use)
> [!CAUTION]
> TO BE MIGRATED TO `settings.yaml` -- THESE WILL CHANGE NOTHING PRESENTLY

spotify-aac-downloader can be configured using the command line arguments or the config file. The config file is created automatically when you run spotify-aac-downloader for the first time at `~/.spotify-aac-downloader/config.json` on Linux and `%USERPROFILE%\.spotify-aac-downloader\config.json` on Windows. Config file values can be overridden using command line arguments.
| Command line argument / Config file key                         | Description                                                           | Default value                                       |
| --------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------- |
| `-c`, `--cookies-location` / `cookies_location`                 | Location of the cookies file.                                         | `./cookies.txt`                                     |
| `-w`, `--po-token` / `po_token`                                 | PO Token for your Youtube Music account                                            | `null`                                              |
| `--config-location` / -                                         | Location of the config file.                                          | `<home_folder>/.spotify-aac-downloader/config.json` |
| `-l`, `--log-level` / `log_level`                               | Log level.                                                            | `INFO`                                              |
| `-n`, `--no-lrc` / `no_lrc`                                     | Don't download the synced lyrics.                                     | `false`                                             |
| `-o`, `--overwrite` / `overwrite`                               | Overwrite existing files.                                             | `false`                                             |
| `--print-exceptions` / `print_exceptions`                       | Print exceptions.                                                     | `false`                                             |
| `-u`, `--url-txt` / -                                           | Read URLs as location of text files containing URLs.                  | `false`                                             |
| `-n`, `--no-config-file` / -                                    | Don't use the config file.                                            | `false`                                             |
