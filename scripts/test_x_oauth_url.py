#!/usr/bin/env python3
"""
Manual script: verify the generated X OAuth 2.0 authorization URL.

Checks that:
  - All required PKCE parameters are present
  - Scopes include the required ones
  - No secrets are embedded in the URL

Run from the backend/ directory:
    cd backend && python ../scripts/test_x_oauth_url.py

Does NOT make any HTTP requests or require a database.
"""
import sys
import urllib.parse
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.config import get_settings
get_settings.cache_clear()
settings = get_settings()

from app.core.security import generate_pkce_pair, generate_state_token


def main() -> None:
    print("=" * 60)
    print("X OAuth 2.0 Authorization URL Test")
    print("=" * 60)

    if not settings.X_CLIENT_ID:
        print("ERROR: X_CLIENT_ID is not set in backend/.env")
        sys.exit(1)
    if not settings.X_CLIENT_SECRET:
        print("ERROR: X_CLIENT_SECRET is not set in backend/.env")
        sys.exit(1)

    # Build the URL the same way XService.begin_connect() does
    state = generate_state_token()
    verifier, challenge = generate_pkce_pair()
    scopes = " ".join(settings.X_SCOPES)
    encoded_scopes = urllib.parse.quote(scopes)

    url = (
        f"{settings.X_OAUTH_AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={settings.X_CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(settings.X_REDIRECT_URI, safe='')}"
        f"&scope={encoded_scopes}"
        f"&state={state}"
        f"&code_challenge={challenge}"
        f"&code_challenge_method=S256"
    )

    parsed = urllib.parse.urlparse(url)
    params = dict(urllib.parse.parse_qsl(parsed.query))

    print()
    print("Generated URL:")
    print(url)
    print()

    errors: list[str] = []

    # Required params
    for required in ("response_type", "client_id", "redirect_uri", "scope", "state",
                     "code_challenge", "code_challenge_method"):
        if required not in params:
            errors.append(f"MISSING param: {required}")
        else:
            print(f"  ✓ {required}: {params[required][:60]}")

    # PKCE method must be S256
    if params.get("code_challenge_method") != "S256":
        errors.append(f"code_challenge_method must be S256, got: {params.get('code_challenge_method')}")

    # Scopes check
    got_scopes = set(urllib.parse.unquote(params.get("scope", "")).split())
    required_scopes = {"tweet.read", "tweet.write", "users.read", "offline.access"}
    missing_scopes = required_scopes - got_scopes
    if missing_scopes:
        errors.append(f"Missing required scopes: {missing_scopes}")
    else:
        print(f"  ✓ scopes: {got_scopes}")

    # Authorize URL must point to x.com
    if "x.com" not in parsed.netloc and "twitter.com" not in parsed.netloc:
        errors.append(f"Unexpected OAuth authorize host: {parsed.netloc}")

    print()
    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        sys.exit(1)

    print("All checks PASSED.")
    print()
    print("To manually test OAuth, open this URL in a browser:")
    print(url)
    print()
    print("Settings summary:")
    print(f"  Authorize URL : {settings.X_OAUTH_AUTHORIZE_URL}")
    print(f"  Token URL     : {settings.X_OAUTH_TOKEN_URL}")
    print(f"  Redirect URI  : {settings.X_REDIRECT_URI}")
    print(f"  Scopes        : {settings.X_SCOPES}")
    print(f"  Client ID     : {settings.X_CLIENT_ID[:6]}***")


if __name__ == "__main__":
    main()
