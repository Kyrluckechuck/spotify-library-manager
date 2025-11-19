"""
Authentication routes for Spotify OAuth.

Provides endpoints for initiating OAuth flow, handling callbacks, and managing tokens.
"""

from typing import Optional

from asgiref.sync import sync_to_async
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.services.spotify_oauth import SpotifyOAuthService

router = APIRouter(prefix="/auth/spotify", tags=["authentication"])


# In-memory state storage (for CSRF protection)
# In production, this should be stored in Redis or similar
_oauth_states: dict[str, bool] = {}


@router.get("/authorize")
async def initiate_oauth(request: Request) -> RedirectResponse:
    """
    Initiate Spotify OAuth flow.

    Redirects user to Spotify authorization page.
    """
    # Construct redirect URI from the request, handling reverse proxy headers
    # Check for X-Forwarded-Host (reverse proxy) first, then fall back to Host header
    host = request.headers.get("x-forwarded-host") or request.headers.get(
        "host", "127.0.0.1:5000"
    )

    # Spotify requires 127.0.0.1 instead of localhost for loopback addresses
    host = host.replace("localhost", "127.0.0.1")

    # Check for X-Forwarded-Proto (reverse proxy) first, then fall back to request scheme
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)

    redirect_uri = f"{scheme}://{host}/auth/spotify/callback"

    auth_url, state = SpotifyOAuthService.get_authorization_url(
        redirect_uri=redirect_uri
    )

    # Store state for validation
    _oauth_states[state] = True

    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
) -> HTMLResponse:
    """
    Handle Spotify OAuth callback.

    Exchanges authorization code for tokens and stores them.
    """
    # Handle authorization errors
    if error:
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 3rem;
                            border-radius: 1rem;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            text-align: center;
                            max-width: 400px;
                        }}
                        h1 {{
                            color: #e74c3c;
                            margin-bottom: 1rem;
                            font-size: 2rem;
                        }}
                        p {{
                            color: #666;
                            line-height: 1.6;
                        }}
                        .error-icon {{
                            width: 80px;
                            height: 80px;
                            margin: 0 auto 1.5rem;
                            background: #e74c3c;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 3rem;
                            color: white;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">✕</div>
                        <h1>Authorization Failed</h1>
                        <p>Error: {error}</p>
                        <p style="font-size: 0.875rem; color: #999; margin-top: 2rem;">You can close this window.</p>
                    </div>
                </body>
            </html>
            """,
            status_code=400,
        )

    # Validate required parameters
    if not code or not state:
        raise HTTPException(
            status_code=400, detail="Missing authorization code or state"
        )

    # Validate state (CSRF protection)
    if state not in _oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    # Remove used state
    del _oauth_states[state]

    # Construct redirect URI from the request (must match authorization request)
    host = request.headers.get("x-forwarded-host") or request.headers.get(
        "host", "127.0.0.1:5000"
    )
    host = host.replace("localhost", "127.0.0.1")
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    redirect_uri = f"{scheme}://{host}/auth/spotify/callback"

    try:
        # Exchange code for tokens
        token_data = SpotifyOAuthService.exchange_code_for_tokens(code, redirect_uri)

        # Save tokens to database
        await sync_to_async(SpotifyOAuthService.save_tokens)(token_data)

        # Success response
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            background: white;
                            padding: 3rem;
                            border-radius: 1rem;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            text-align: center;
                            max-width: 400px;
                        }
                        h1 {
                            color: #1DB954;
                            margin-bottom: 1rem;
                            font-size: 2rem;
                        }
                        p {
                            color: #666;
                            margin-bottom: 2rem;
                            line-height: 1.6;
                        }
                        .button {
                            display: inline-block;
                            background: #1DB954;
                            color: white;
                            padding: 1rem 2rem;
                            border-radius: 2rem;
                            text-decoration: none;
                            font-weight: 600;
                            transition: background 0.3s;
                        }
                        .button:hover {
                            background: #1ed760;
                        }
                        .checkmark {
                            width: 80px;
                            height: 80px;
                            margin: 0 auto 1.5rem;
                            background: #1DB954;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        .checkmark svg {
                            width: 50px;
                            height: 50px;
                            fill: white;
                        }
                    </style>
                    <script>
                        // Close window immediately after success
                        window.close();
                        // If window.close() didn't work (some browsers block it),
                        // show a message to manually close
                        setTimeout(() => {
                            if (!window.closed) {
                                document.getElementById('auto-close-msg').style.display = 'none';
                                document.getElementById('manual-close-msg').style.display = 'block';
                            }
                        }, 100);
                    </script>
                </head>
                <body>
                    <div class="container">
                        <div class="checkmark">
                            <svg viewBox="0 0 24 24">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                        </div>
                        <h1>Successfully Connected!</h1>
                        <p>Your Spotify account has been linked. You can now access private playlists.</p>
                        <p id="auto-close-msg" style="font-size: 0.875rem; color: #999;">Closing window...</p>
                        <p id="manual-close-msg" style="font-size: 0.875rem; color: #999; display: none;">You can close this window now.</p>
                    </div>
                </body>
            </html>
            """
        )

    except Exception as e:
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }}
                        .container {{
                            background: white;
                            padding: 3rem;
                            border-radius: 1rem;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            text-align: center;
                            max-width: 400px;
                        }}
                        h1 {{
                            color: #e74c3c;
                            margin-bottom: 1rem;
                            font-size: 2rem;
                        }}
                        p {{
                            color: #666;
                            line-height: 1.6;
                        }}
                        .error-icon {{
                            width: 80px;
                            height: 80px;
                            margin: 0 auto 1.5rem;
                            background: #e74c3c;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 3rem;
                            color: white;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error-icon">✕</div>
                        <h1>Connection Failed</h1>
                        <p>Failed to exchange authorization code for tokens.</p>
                        <p style="font-size: 0.875rem; color: #999;">Error: {str(e)}</p>
                        <p style="font-size: 0.875rem; color: #999; margin-top: 2rem;">You can close this window and try again.</p>
                    </div>
                </body>
            </html>
            """,
            status_code=500,
        )


@router.delete("/disconnect")
async def disconnect_spotify() -> dict[str, str]:
    """
    Disconnect Spotify account by removing stored tokens.
    """
    await sync_to_async(SpotifyOAuthService.revoke_tokens)()
    return {"message": "Spotify account disconnected successfully"}


@router.get("/status")
async def oauth_status() -> dict[str, bool]:
    """
    Check if user is authenticated with Spotify OAuth.
    """
    is_authenticated = await SpotifyOAuthService.is_authenticated()
    return {"authenticated": is_authenticated}
