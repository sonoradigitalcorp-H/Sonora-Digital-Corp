"""Supabase client integration [FR1] — Auth + Storage wrapper."""

import json
import logging
import os
from typing import Any

import httpx

log = logging.getLogger("sonora.engine.supabase")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


class SupabaseAuth:
    """Supabase Auth wrapper — login, signup, session verification."""

    def __init__(self):
        self.url = SUPABASE_URL.rstrip("/")
        self.headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        }

    def sign_in_with_google(self) -> str:
        """Get Google OAuth URL for sign-in."""
        redirect_to = os.getenv("APP_URL", "http://localhost:5100")
        return (
            f"{self.url}/auth/v1/authorize"
            f"?provider=google"
            f"&redirect_to={redirect_to}/auth/callback"
        )

    async def sign_in_with_email(self, email: str, password: str) -> dict[str, Any]:
        """Sign in with email/password."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.url}/auth/v1/token?grant_type=password",
                headers=self.headers,
                json={"email": email, "password": password},
            )
            return resp.json()

    async def sign_up(self, email: str, password: str, metadata: dict | None = None) -> dict[str, Any]:
        """Sign up with email/password."""
        payload = {"email": email, "password": password}
        if metadata:
            payload["data"] = metadata

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.url}/auth/v1/signup",
                headers=self.headers,
                json=payload,
            )
            return resp.json()

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify a Supabase JWT and extract user info.

        Returns:
            {sub, email, role, tenant_id} or None if invalid
        """
        try:
            import jwt as pyjwt

            payload = pyjwt.decode(
                token,
                SUPABASE_ANON_KEY,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return {
                "sub": payload.get("sub"),
                "email": payload.get("email", ""),
                "role": payload.get("role", "authenticated"),
                "user_metadata": payload.get("user_metadata", {}),
            }
        except Exception as e:
            log.warning(f"Token verification failed: {e}")
            return None

    async def get_user(self, token: str) -> dict[str, Any] | None:
        """Get user info from Supabase Auth."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.url}/auth/v1/user",
                headers={**self.headers, "Authorization": f"Bearer {token}"},
            )
            if resp.status_code == 200:
                return resp.json()
            return None


class SupabaseStorage:
    """Supabase Storage wrapper — file uploads for greetings, avatars, content."""

    def __init__(self):
        self.url = SUPABASE_URL.rstrip("/")
        self.headers = {
            "apikey": SUPABASE_ANON_KEY,
        }

    async def upload_file(
        self, bucket: str, path: str, content: bytes, content_type: str
    ) -> str | None:
        """Upload a file to Supabase Storage.

        Returns:
            Public URL of the uploaded file, or None on failure.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.url}/storage/v1/object/{bucket}/{path}",
                headers={
                    **self.headers,
                    "Content-Type": content_type,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
                content=content,
            )
            if resp.status_code in (200, 201):
                return f"{self.url}/storage/v1/object/public/{bucket}/{path}"
            log.error(f"Upload failed: {resp.status_code} {resp.text}")
            return None

    async def upload_greeting_audio(
        self, tenant_id: str, greeting_id: str, audio_bytes: bytes
    ) -> str | None:
        """Upload greeting audio to tenant's bucket."""
        return await self.upload_file(
            bucket=f"{tenant_id}-greetings",
            path=f"{greeting_id}.mp3",
            content=audio_bytes,
            content_type="audio/mpeg",
        )

    async def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file."""
        return f"{self.url}/storage/v1/object/public/{bucket}/{path}"


# Singleton instances
auth = SupabaseAuth()
storage = SupabaseStorage()
