#!/usr/bin/env python3
"""
Manual script: publish a real test tweet to X.

REQUIREMENTS:
  - backend/.env: ENABLE_REAL_X_API=true, MOCK_MODE=false
  - A connected X account in the database (run OAuth flow first)
  - PostgreSQL running with a populated users + x_accounts table

SAFETY:
  - Asks for explicit "yes" confirmation before publishing
  - Test text clearly identifies this as an API integration test
  - Never runs automatically; must be triggered by hand

Run from the backend/ directory:
    cd backend && python ../scripts/test_x_real_text_publish.py --user-email you@example.com
"""
import argparse
import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.config import get_settings
get_settings.cache_clear()
settings = get_settings()


async def main(user_email: str) -> None:
    print("=" * 60)
    print("X Real Text Publish Test")
    print("=" * 60)

    if settings.MOCK_MODE:
        print("ERROR: MOCK_MODE=true — set to false in backend/.env")
        sys.exit(1)
    if not settings.ENABLE_REAL_X_API:
        print("ERROR: ENABLE_REAL_X_API=false — set to true in backend/.env")
        sys.exit(1)

    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from app.models.x_account import XAccount
    from app.core.security import decrypt_secret

    test_text = (
        "[API Integration Test] This tweet was published automatically "
        "by the Agentic X Content Platform test script. "
        "It confirms real X OAuth + posting is working. "
        "Please ignore or delete."
    )

    print()
    print(f"User email  : {user_email}")
    print(f"Test tweet  : {test_text}")
    print()
    answer = input("Type 'yes' to publish this tweet → ").strip().lower()
    if answer != "yes":
        print("Aborted. Nothing was published.")
        sys.exit(0)

    async with AsyncSessionLocal() as session:
        user_row = (
            await session.execute(select(User).where(User.email == user_email))
        ).scalar_one_or_none()
        if not user_row:
            print(f"ERROR: No user found with email {user_email}")
            sys.exit(1)

        account = (
            await session.execute(
                select(XAccount).where(XAccount.user_id == user_row.id)
            )
        ).scalar_one_or_none()
        if not account:
            print("ERROR: No connected X account for this user. Run the OAuth flow first.")
            sys.exit(1)

        print()
        print(f"Connected X account : @{account.username} ({account.x_user_id})")

        import httpx
        from app.services.x_service import XService

        service = XService(session)
        access_token = await service._get_valid_token(account)

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{settings.X_API_BASE_URL}/tweets",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"text": test_text},
            )

        if response.status_code >= 400:
            print(f"ERROR: X API returned {response.status_code}: {response.text}")
            sys.exit(1)

        data = response.json().get("data", {})
        post_id = data.get("id")
        print()
        print(f"Published successfully!")
        print(f"Post ID  : {post_id}")
        print(f"URL      : https://x.com/i/web/status/{post_id}")
        print()
        print("Test PASSED.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish a real test tweet to X.")
    parser.add_argument(
        "--user-email",
        required=True,
        help="Email of the user whose connected X account will be used.",
    )
    args = parser.parse_args()
    asyncio.run(main(args.user_email))
