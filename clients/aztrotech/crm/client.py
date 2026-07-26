#!/usr/bin/env python3
"""
CRM Client — unified interface for contact management.

Usage:
    python3 -m clients.aztrotech.crm.client add --name "Juan Perez" --phone "5216621234567" --company "Empresa"
    python3 -m clients.aztrotech.crm.client search --query "Juan"
    python3 -m clients.aztrotech.crm.client list
    python3 -m clients.aztrotech.crm.client get --id CT-1234567890-abc12345
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from clients.aztrotech.crm.models import Contact
from clients.aztrotech.crm.store import CRMStore
from clients.aztrotech.crm.search import CRMSearch
from clients.aztrotech.crm.sync import CRMSync


def cmd_add(args):
    store = CRMStore()
    search = CRMSearch(store)
    sync = CRMSync(store, tenant=args.tenant)

    contact = Contact(
        name=args.name,
        phone=args.phone,
        company=args.company,
        email=args.email or "",
        instagram=args.instagram or "",
        source=args.source or "manual",
        tags=args.tags or "",
        notes=args.notes or "",
    )

    store.upsert(contact)
    sync.sync_all(contact)
    print(json.dumps(contact.to_dict(), ensure_ascii=False, indent=2))
    return contact


def cmd_search(args):
    store = CRMStore()
    search = CRMSearch(store)
    results = search.search(args.query, limit=args.limit)
    for c in results:
        print(f"  {c.crm_id[-12:]} | {c.name:20s} | {c.phone:15s} | {c.company[:20]:20s}")
    print(f"  → {len(results)} results")


def cmd_list(args):
    store = CRMStore()
    contacts = store.list_all(limit=args.limit)
    for c in contacts:
        print(f"  {c.crm_id[-12:]} | {c.name:20s} | {c.phone:15s} | {c.company[:20]:20s}")
    print(f"  → {len(contacts)} total (showing {min(len(contacts), args.limit)})")


def cmd_get(args):
    store = CRMStore()
    contact = store.get(args.id)
    if contact:
        print(json.dumps(contact.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Contact not found: {args.id}")
        sys.exit(1)


def cmd_sync(args):
    store = CRMStore()
    sync = CRMSync(store, tenant=args.tenant)
    contact = store.get(args.id)
    if contact:
        sync.sync_all(contact)
        print(f"Synced: {contact.crm_id}")
    else:
        print(f"Contact not found: {args.id}")
        sys.exit(1)


def cmd_sync_all(args):
    store = CRMStore()
    sync = CRMSync(store, tenant=args.tenant)
    contacts = store.list_all(limit=10000)
    for c in contacts:
        sync.sync_all(c)
    print(f"Synced {len(contacts)} contacts to all stores")


def main():
    parser = argparse.ArgumentParser(description="AztroTech CRM")
    parser.add_argument("--tenant", default="aztrotech", help="Tenant ID")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add/update contact")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--phone", required=True)
    p_add.add_argument("--company", default="")
    p_add.add_argument("--email", default="")
    p_add.add_argument("--instagram", default="")
    p_add.add_argument("--source", default="manual")
    p_add.add_argument("--tags", default="")
    p_add.add_argument("--notes", default="")

    p_search = sub.add_parser("search", help="Search contacts")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=20)

    p_list = sub.add_parser("list", help="List contacts")
    p_list.add_argument("--limit", type=int, default=50)

    p_get = sub.add_parser("get", help="Get contact by ID")
    p_get.add_argument("--id", required=True)

    p_sync = sub.add_parser("sync", help="Sync contact to all stores")
    p_sync.add_argument("--id", required=True)

    p_sync_all = sub.add_parser("sync-all", help="Sync all contacts")
    p_sync_all.add_argument("--tenant", default="aztrotech")

    args = parser.parse_args()
    if args.command == "add":
        cmd_add(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "sync":
        cmd_sync(args)
    elif args.command == "sync-all":
        cmd_sync_all(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
