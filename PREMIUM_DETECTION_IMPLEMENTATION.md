# Premium Detection Implementation

## Overview

This implementation adds comprehensive premium status detection and quality validation to the Spotify Library Manager. It addresses the issue where users couldn't detect when their YouTube Premium cookies or PO token expired and was causing requests to fallback to "free" quality downloads.

## Key Features

### 1. Multi-Method Premium Detection

The `PremiumDetector` class uses three detection methods with confidence scoring:

1. **Account Info Detection** (Highest confidence: 0.9)
   - Uses `ytmusicapi.get_account_info()` to check for premium indicators
   - Looks for fields like `isPremium`, `subscriptionType`, `membershipType`

2. **Quality Probe Detection** (Medium confidence: 0.7)
   - Tests actual available qualities for popular songs
   - Detects if 256kbps+ formats are available (premium indicator)

3. **Chart Access Detection** (Lower confidence: 0.8)
   - Checks access to premium-only chart features
   - Premium users get more detailed chart information

### 2. Smart Bitrate Validation

Instead of simply checking if download is 128kbps vs 256kbps:
- Validates actual available qualities for each specific song
- Some songs only have 128kbps maximum even for premium users
- Provides detailed error messages explaining why quality is lower

### 3. Premium Expiry Detection

Automatically detects when premium has expired:
- Compares expected vs actual download quality
- Checks if song actually has higher quality available
- Refreshes premium status when expiry is detected
- Logs detailed warnings about potential cookie/token expiry

### 4. Caching and Performance

- 5-minute cache for premium status to avoid repeated API calls
- Force refresh option when expiry is detected
- Graceful fallback when API calls fail

## Implementation Details

### New Files

1. **`api/downloader/premium_detector.py`**
   - Core premium detection logic
   - Multi-method detection with confidence scoring
   - Quality validation and expiry detection

2. **`api/tests/unit/test_premium_detector.py`**
   - Comprehensive unit tests for all detection methods
   - Tests error handling and edge cases

3. **`api/tests/integration/test_premium_detector_integration.py`**
   - Integration tests with real API scenarios
   - Tests caching behavior and multi-method fallback

4. **`api/tests/integration/test_spotdl_wrapper_premium_integration.py`**
   - Tests SpotdlWrapper integration with premium detection
   - Validates bitrate logic and expiry detection

### Modified Files

1. **`requirements.txt`**
   - Added `ytmusicapi>=1.8.0` dependency

2. **`api/downloader/spotdl_wrapper.py`**
   - Integrated PremiumDetector in initialization
   - Updated bitrate validation logic to use premium detection
   - Added premium expiry detection during downloads
   - Improved error messages with quality information

## Usage Examples

### Basic Premium Detection

```python
from downloader.premium_detector import PremiumDetector

# Initialize with YouTube credentials
detector = PremiumDetector(
    cookies_file="/path/to/cookies.txt",
    po_token="your_po_token"
)

# Detect premium status
status = detector.detect_premium_status()
print(f"Premium: {status.is_premium}")
print(f"Confidence: {status.confidence}")
print(f"Method: {status.detection_method}")
```

### Song Quality Validation

```python
# Check available qualities for a specific song
qualities = detector.get_song_available_qualities(
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
)
print(f"Available: {qualities}")  # [(256, "AAC"), (128, "AAC")]
```

### Premium Expiry Detection

```python
# Check if premium has expired based on download quality
is_expired, reason = detector.is_premium_expired(
    downloaded_bitrate=128,
    expected_premium_bitrate=256
)
if is_expired:
    print(f"Premium expired: {reason}")
```

## Error Handling

The implementation includes comprehensive error handling:

1. **Graceful Degradation**: If premium detection fails, defaults to free user expectations
2. **Multiple Fallbacks**: Uses up to 3 detection methods for reliability
3. **Detailed Logging**: Provides clear error messages and warnings
4. **No Breaking Changes**: Existing functionality continues to work if premium detection fails

## Quality Validation Logic

### Before (Old Logic)
```python
expected_bitrate = 255 if (cookies and po_token) else 127
```

### After (New Logic)
```python
# Get actual available qualities for this specific song
available_qualities = detector.get_song_available_qualities(spotify_url)
max_available = max([q[0] for q in available_qualities])

# Set expectation based on premium status AND song availability
if premium_status.is_premium and premium_status.confidence > 0.7:
    expected_bitrate = min(255, max_available)  # Premium: up to 256kbps or song max
else:
    expected_bitrate = min(127, max_available)  # Free: up to 128kbps or song max
```

## Benefits

1. **Accurate Premium Detection**: No more false assumptions based on cookie/token presence
2. **Song-Specific Validation**: Understands that some songs only have lower quality available
3. **Automatic Expiry Detection**: Alerts users when premium credentials need refreshing
4. **Better Error Messages**: Clear explanations of why quality is lower than expected
5. **Non-Breaking**: Maintains backward compatibility with existing code

## Future Enhancements

Potential improvements for future versions:

1. **Spotify Integration**: Use Spotify API to get song quality metadata
2. **User Notifications**: Add UI notifications for premium expiry
3. **Automatic Refresh**: Implement automatic cookie/token refresh workflows
4. **Quality Preferences**: Allow users to set minimum acceptable quality thresholds
5. **Analytics**: Track premium detection accuracy and false positives

## Testing

Run the test suite to verify functionality:

```bash
# Unit tests (requires database setup)
python -m pytest api/tests/unit/test_premium_detector.py

# Integration tests
python -m pytest api/tests/integration/test_premium_detector_integration.py

# SpotdlWrapper integration tests
python -m pytest api/tests/integration/test_spotdl_wrapper_premium_integration.py
```

## Dependencies

- `ytmusicapi>=1.8.0`: YouTube Music API client for premium detection
- `typing`: Type hints for better code quality
- `dataclasses`: For structured status objects
- `logging`: Comprehensive logging throughout detection process

## Configuration

No additional configuration required. The premium detector automatically uses:
- `config.cookies_location`: Path to YouTube cookies file
- `config.po_token`: YouTube PO token for authentication

Both are optional - the detector gracefully handles missing credentials.
