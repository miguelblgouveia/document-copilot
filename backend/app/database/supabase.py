from __future__ import annotations

import asyncio

from supabase import AsyncClient, AsyncClientOptions, acreate_client

from app.config import settings

_service_role_client: AsyncClient | None = None
_service_role_lock = asyncio.Lock()


def _build_client_options(access_token: str | None = None) -> AsyncClientOptions:
    headers: dict[str, str] = {}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token}"

    return AsyncClientOptions(
        auto_refresh_token=False,
        persist_session=False,
        headers=headers,
    )


async def create_user_supabase_client(access_token: str) -> AsyncClient:
    """Create a request-scoped client that enforces the caller's RLS policies."""
    token = access_token.strip()
    if not token:
        raise ValueError("access_token must not be empty")

    return await acreate_client(
        str(settings.supabase_url),
        settings.supabase_anon_key.get_secret_value(),
        options=_build_client_options(token),
    )


async def get_service_role_supabase_client() -> AsyncClient:
    """Return a cached backend-only client for privileged Supabase operations."""
    global _service_role_client

    if _service_role_client is None:
        async with _service_role_lock:
            if _service_role_client is None:
                _service_role_client = await acreate_client(
                    str(settings.supabase_url),
                    settings.supabase_service_role_key.get_secret_value(),
                    options=_build_client_options(),
                )

    return _service_role_client


__all__ = ["create_user_supabase_client", "get_service_role_supabase_client"]