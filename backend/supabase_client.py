"""
Supabase client singleton.

Uses the service_role key on the backend so we can read/write all tables
(RLS is still enabled for defense-in-depth / PostgREST anon access).
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


@lru_cache
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")  # prefer service_role for backend
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment / .env"
        )
    return create_client(url, key)
