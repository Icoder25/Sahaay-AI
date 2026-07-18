"""Trusted server-side Supabase client."""

from functools import lru_cache

from supabase import Client, create_client

from app.config import get_settings


class SupabaseConfigurationError(RuntimeError):
    """Raised when server-side Supabase credentials are missing."""


@lru_cache(maxsize=1)
def get_supabase_admin_client() -> Client:
    """Return a service-role Supabase client that must never reach a browser."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseConfigurationError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required"
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
