from urllib.parse import urljoin, urlparse
import base62
from datetime import datetime

from lib.config_class import Config

def convert_date_string_to_datetime(string):
    added_at: str = string
    # Convert from Zulu UTC to datetime UTC
    added_at = added_at.replace('Z', '+00:00')
    return datetime.fromisoformat(added_at)

def update_process_info(config: Config, progress: int):
    if config.process_info is None:
        return
    config.process_info.total_progress = progress
    config.process_info.update(n=0)

def uri_to_gid(uri: str) -> str:
    return hex(base62.decode(uri, base62.CHARSET_INVERTED))[2:].zfill(32)

def gid_to_uri(gid: str) -> str:
    return base62.encode(int(gid, 16), charset=base62.CHARSET_INVERTED).zfill(22)

def sanitize_and_strip_url(raw_url: str) -> str:
    raw_url = raw_url.strip()

    # Strip "personalized" tokens spotify auto-inserts into http URLs (Not applicable to URIs)
    if (raw_url.startswith('http')):
        raw_url = urljoin(raw_url, urlparse(raw_url).path)
    
    return raw_url