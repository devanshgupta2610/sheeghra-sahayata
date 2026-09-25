#!/usr/bin/env python3
"""
==========================================================================
PRIVACY-BY-DESIGN — Location cleanup job (hackathon judging highlight)
==========================================================================

Deletes location breadcrumbs once a trip has ended, UNLESS that location
is linked to an incident (incident_id IS NOT NULL). SOS-linked GPS fixes
are retained as evidence for authorities.

Run modes:
  1. Local / Railway cron:  python scripts/cleanup_locations.py
  2. Or schedule via Supabase pg_cron (see SQL at bottom of this file)

This is intentional privacy architecture: we do NOT keep a tourist's
movement history after the trip ends.
==========================================================================
"""

import os
import sys

# Allow running from repo root or from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from supabase_client import get_supabase  # noqa: E402


def cleanup_ended_trip_locations() -> dict:
    sb = get_supabase()

    # Find ended trips
    ended = sb.table("trips").select("id").eq("status", "ended").execute()
    ended_ids = [t["id"] for t in (ended.data or [])]
    if not ended_ids:
        print("[privacy-cleanup] No ended trips — nothing to purge.")
        return {"deleted": 0, "retained_for_incidents": 0}

    deleted = 0
    retained = 0

    for trip_id in ended_ids:
        # Locations NOT linked to an incident → safe to delete
        purge = (
            sb.table("locations")
            .delete()
            .eq("trip_id", trip_id)
            .is_("incident_id", "null")
            .execute()
        )
        # supabase-py returns deleted rows in .data when available
        n = len(purge.data) if purge.data else 0
        deleted += n

        keep = (
            sb.table("locations")
            .select("id")
            .eq("trip_id", trip_id)
            .not_.is_("incident_id", "null")
            .execute()
        )
        retained += len(keep.data or [])

    summary = {
        "deleted": deleted,
        "retained_for_incidents": retained,
        "ended_trips_scanned": len(ended_ids),
    }
    print(f"[privacy-cleanup] {summary}")
    return summary


if __name__ == "__main__":
    cleanup_ended_trip_locations()


# ---------------------------------------------------------------------------
# Optional Supabase pg_cron equivalent (run once in SQL Editor):
#
#   create extension if not exists pg_cron;
#
#   select cron.schedule(
#     'purge-ended-trip-locations',
#     '*/15 * * * *',  -- every 15 minutes
#     $$
#       DELETE FROM locations
#       WHERE incident_id IS NULL
#         AND trip_id IN (SELECT id FROM trips WHERE status = 'ended');
#     $$
#   );
# ---------------------------------------------------------------------------
