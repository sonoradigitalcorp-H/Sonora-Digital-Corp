#!/usr/bin/env python3
"""Migrate ABE Music JSON data → Hasura/PostgreSQL.

Usage: python3 scripts/migrate_abe_to_hasura.py [--tenant abe-music]
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("migrate")

REPO = Path(__file__).resolve().parent.parent
DATA_DIR = REPO / "data"

# Hasura client
sys.path.insert(0, str(REPO))


def hasura_mutate(query: str, variables: dict) -> dict:
    """Execute Hasura mutation."""
    from apps.sonora_engine.hasura import mutate
    return mutate(query, variables)


def load_json(filename: str) -> dict:
    path = DATA_DIR / filename
    if not path.exists():
        log.warning(f"File not found: {path}")
        return {}
    with open(path) as f:
        return json.load(f)


def migrate_artists(tenant_id: str) -> dict[str, str]:
    """Migrate artists from abe-music.json → artists table."""
    data = load_json("abe-music.json")
    artists_data = data.get("artists", {})
    legacy_map = {}

    for legacy_id, artist in artists_data.items():
        try:
            result = hasura_mutate("""
                mutation MigrateArtist($artist: artists_insert_input!) {
                    insert_artists_one(object: $artist) { id }
                }
            """, {
                "artist": {
                    "tenant_id": tenant_id,
                    "legacy_id": legacy_id,
                    "name": artist.get("nombre", artist.get("name", "Unknown")),
                    "genre": artist.get("genero", ""),
                    "country": artist.get("pais", ""),
                    "status": artist.get("status", "active"),
                    "email": artist.get("email", ""),
                    "phone": artist.get("telefono", ""),
                    "streams": artist.get("streams", 0),
                    "revenue": artist.get("revenue", 0),
                    "monthly_listeners": artist.get("monthly_listeners", 0),
                    "followers": artist.get("followers", 0),
                    "top_song": artist.get("top_song", ""),
                    "top_song_streams": artist.get("top_song_streams", 0),
                    "youtube_views": artist.get("youtube_views", 0),
                    "releases_count": artist.get("releases_count", 0),
                    "spotify_url": artist.get("spotify_url", ""),
                    "apple_music_url": artist.get("apple_music_url", ""),
                    "label": artist.get("label", ""),
                    "distribution": artist.get("distribution", ""),
                    "notable": artist.get("notable", ""),
                    "social": json.dumps({
                        "instagram": artist.get("instagram", ""),
                        "tiktok": artist.get("tiktok", ""),
                    }),
                    "metadata": json.dumps({
                        "nb_album": artist.get("nb_album", 0),
                        "latest_release": artist.get("latest_release", ""),
                        "from": artist.get("from", ""),
                    }),
                }
            })
            new_id = result.get("data", {}).get("insert_artists_one", {}).get("id")
            if new_id:
                legacy_map[legacy_id] = new_id
                log.info(f"  Migrated artist: {artist.get('nombre', 'Unknown')} → {new_id}")
        except Exception as e:
            log.error(f"  Failed to migrate artist {legacy_id}: {e}")

    return legacy_map


def migrate_contracts(tenant_id: str, legacy_artist_map: dict[str, str]) -> dict[str, str]:
    """Migrate contracts from abe-contracts.json → contracts table."""
    data = load_json("abe-contracts.json")
    contracts_data = data.get("contracts", {})
    legacy_map = {}

    for legacy_id, contract in contracts_data.items():
        artist_legacy_id = contract.get("artist_id", "")
        artist_uuid = legacy_artist_map.get(artist_legacy_id)

        if not artist_uuid:
            log.warning(f"  Skipping contract {legacy_id}: no migrated artist for {artist_legacy_id}")
            continue

        splits = contract.get("revenue_splits", {})

        try:
            result = hasura_mutate("""
                mutation MigrateContract($contract: contracts_insert_input!) {
                    insert_contracts_one(object: $contract) { id }
                }
            """, {
                "contract": {
                    "tenant_id": tenant_id,
                    "artist_id": artist_uuid,
                    "type": contract.get("type", "distribution_only"),
                    "status": contract.get("status", "draft"),
                    "start_date": contract.get("start_date", datetime.now().isoformat()),
                    "end_date": contract.get("end_date"),
                    "revenue_splits": json.dumps(splits),
                    "territories": contract.get("territories", ["worldwide"]),
                    "platforms": contract.get("platforms", ["all"]),
                }
            })
            new_id = result.get("data", {}).get("insert_contracts_one", {}).get("id")
            if new_id:
                legacy_map[legacy_id] = new_id
                log.info(f"  Migrated contract {legacy_id} → {new_id}")
        except Exception as e:
            log.error(f"  Failed to migrate contract {legacy_id}: {e}")

    return legacy_map


def migrate_revenue(tenant_id: str, legacy_contract_map: dict[str, str], legacy_artist_map: dict[str, str]):
    """Migrate revenue entries from abe-ledger.json → revenue_entries table."""
    data = load_json("abe-ledger.json")
    entries = data.get("entries", [])

    for entry in entries:
        contract_id = legacy_contract_map.get(entry.get("contract_id", ""), entry.get("contract_id"))
        artist_id = legacy_artist_map.get(entry.get("artist_id", ""), entry.get("artist_id"))
        split = entry.get("split", {})

        try:
            result = hasura_mutate("""
                mutation MigrateRevenue($entry: revenue_entries_insert_input!) {
                    insert_revenue_entries_one(object: $entry) { id }
                }
            """, {
                "entry": {
                    "tenant_id": tenant_id,
                    "contract_id": contract_id,
                    "artist_id": artist_id,
                    "release_id": entry.get("release_id"),
                    "amount": entry.get("amount", 0),
                    "source": entry.get("source", "streaming"),
                    "split_snapshot": json.dumps(split),
                    "artist_share": entry.get("artist_share", 0),
                    "label_share": entry.get("label_share", 0),
                    "distributor_share": entry.get("distributor_share", 0),
                    "recorded_at": entry.get("timestamp", datetime.now().isoformat()),
                }
            })
            log.info(f"  Migrated revenue entry: ${entry.get('amount', 0)}")
        except Exception as e:
            log.error(f"  Failed to migrate revenue entry: {e}")


def main():
    parser = argparse.ArgumentParser(description="Migrate ABE JSON data to Hasura")
    parser.add_argument("--tenant", default="abe-music", help="Tenant slug (default: abe-music)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without writing")
    args = parser.parse_args()

    log.info(f"Migrating ABE data to Hasura for tenant: {args.tenant}")

    # Get tenant UUID from Hasura
    from apps.sonora_engine.hasura import query
    result = query("""
        query GetTenant($slug: String!) {
            tenants(where: {slug: {_eq: $slug}}) { id }
        }
    """, {"slug": args.tenant})

    tenants = result.get("data", {}).get("tenants", [])
    if not tenants:
        log.error(f"Tenant '{args.tenant}' not found in Hasura. Run migration 010 first.")
        sys.exit(1)

    tenant_id = tenants[0]["id"]
    log.info(f"Tenant ID: {tenant_id}")

    if args.dry_run:
        log.info("DRY RUN — checking source data...")
        for f in ["abe-music.json", "abe-contracts.json", "abe-ledger.json"]:
            data = load_json(f)
            if f == "abe-music.json":
                artists = data.get("artists", {})
                log.info(f"  {f}: {len(artists)} artists found")
            elif f == "abe-contracts.json":
                contracts = data.get("contracts", {})
                log.info(f"  {f}: {len(contracts)} contracts found")
            elif f == "abe-ledger.json":
                entries = data.get("entries", [])
                log.info(f"  {f}: {len(entries)} revenue entries found")
        log.info("Dry run complete. Run without --dry-run to execute migration.")
        return

    # Phase 1: Migrate artists
    log.info("Phase 1: Migrating artists...")
    legacy_artist_map = migrate_artists(tenant_id)
    log.info(f"  → {len(legacy_artist_map)} artists migrated")

    # Phase 2: Migrate contracts
    log.info("Phase 2: Migrating contracts...")
    legacy_contract_map = migrate_contracts(tenant_id, legacy_artist_map)
    log.info(f"  → {len(legacy_contract_map)} contracts migrated")

    # Phase 3: Migrate revenue entries
    log.info("Phase 3: Migrating revenue entries...")
    migrate_revenue(tenant_id, legacy_contract_map, legacy_artist_map)

    log.info("Migration complete!")


if __name__ == "__main__":
    main()
