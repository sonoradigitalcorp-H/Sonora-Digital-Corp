#!/usr/bin/env python3
"""Link two channel identities as the same user for cross-channel session continuity.

Usage:
    python3 scripts/link-identity.py --telegram 12345 --whatsapp +521555010203
    python3 scripts/link-identity.py --web user@email.com --telegram 12345
    python3 scripts/link-identity.py --whatsapp +521555010203 --voice voice_user_abc
"""

import argparse
import logging
import sys

from platforms.continuity_bridge import ContinuityBridge

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Link two channel identities as the same user for cross-channel continuity.",
    )

    id_group = parser.add_mutually_exclusive_group(required=True)
    id_group.add_argument("--telegram", help="Telegram user ID", metavar="ID")
    id_group.add_argument("--whatsapp", help="WhatsApp phone number", metavar="PHONE")
    id_group.add_argument("--web", help="Web session ID or email", metavar="ID")
    id_group.add_argument("--voice", help="Voice user ID", metavar="ID")

    id2_group = parser.add_mutually_exclusive_group(required=True)
    id2_group.add_argument("--to-telegram", help="Second identity: Telegram user ID", metavar="ID", dest="to_telegram")
    id2_group.add_argument("--to-whatsapp", help="Second identity: WhatsApp phone number", metavar="PHONE", dest="to_whatsapp")
    id2_group.add_argument("--to-web", help="Second identity: Web session ID or email", metavar="ID", dest="to_web")
    id2_group.add_argument("--to-voice", help="Second identity: Voice user ID", metavar="ID", dest="to_voice")

    args = parser.parse_args()

    primary_channel, primary_id = _resolve_identity(args)
    secondary_channel, secondary_id = _resolve_secondary(args)

    if primary_channel is None or secondary_channel is None:
        parser.print_help()
        return 1

    log.info("Linking %s (%s) <-> %s (%s)", primary_channel, primary_id, secondary_channel, secondary_id)

    bridge = ContinuityBridge()
    success = bridge.link_identities(primary_id, secondary_id, primary_channel, secondary_channel)

    if success:
        unified_id = bridge.get_unified_user_id(primary_id, primary_channel)
        log.info("Successfully linked! Unified ID: %s", unified_id)
        print(f"Linked: {primary_channel}/{primary_id} <-> {secondary_channel}/{secondary_id}")
        print(f"Unified User ID: {unified_id}")
        return 0
    else:
        log.error("Failed to link identities (they may already have different unified IDs)")
        return 1


def _resolve_identity(args: argparse.Namespace) -> tuple:
    if args.telegram:
        return "telegram", args.telegram
    if args.whatsapp:
        return "whatsapp", args.whatsapp
    if args.web:
        return "web", args.web
    if args.voice:
        return "voice", args.voice
    return None, None


def _resolve_secondary(args: argparse.Namespace) -> tuple:
    if args.to_telegram:
        return "telegram", args.to_telegram
    if args.to_whatsapp:
        return "whatsapp", args.to_whatsapp
    if args.to_web:
        return "web", args.to_web
    if args.to_voice:
        return "voice", args.to_voice
    return None, None


if __name__ == "__main__":
    sys.exit(main())
