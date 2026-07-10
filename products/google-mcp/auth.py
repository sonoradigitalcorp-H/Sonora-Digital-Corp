#!/usr/bin/env python3
"""
Google Auth Setup — Sonora Digital Corp.

Sets up Google API access on a headless VPS.
Three modes:
  --gemini-key KEY    Set a Gemini API key directly
  --gcloud            Use gcloud CLI auth (prints URL for any device)
  --notebooklm        Interactive notebooklm login (needs display via xvfb)
  --all               Run all available methods
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
MCP_DIR = HOME / ".google_mcp"
MCP_DIR.mkdir(exist_ok=True)

ENV_FILE = HOME / ".hermes" / ".env"


def add_to_env(key: str, value: str):
    """Add or update a key in the .env file."""
    lines = []
    found = False
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    ENV_FILE.write_text("\n".join(lines) + "\n")
    print(f"  ✅ Added {key} to {ENV_FILE}")


def setup_gemini_key(key: str):
    """Direct API key — no browser needed, works immediately."""
    if not key:
        print("  ❌ No key provided. Get one at https://aistudio.google.com/apikey")
        return False
    add_to_env("GEMINI_API_KEY", key)
    os.environ["GEMINI_API_KEY"] = key
    print("  ✅ Gemini API key configured!")
    print("  🧪 Test: python3 -c \"import httpx; r=httpx.get('https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash?key='+os.environ['GEMINI_API_KEY']); print(r.json())\"")
    return True


def setup_gcloud():
    """gcloud auth — prints URL, authenticate from any device."""
    print("\n📡 Setting up Google Cloud auth...")
    try:
        subprocess.run(["gcloud", "--version"],
                       capture_output=True, timeout=5)
    except FileNotFoundError:
        print("  ❌ gcloud CLI not installed.")
        print("  Install: https://cloud.google.com/sdk/docs/install")
        print("  Or: sudo apt-get install google-cloud-sdk")
        return False

    print("\n  📋 Step 1: Open this URL in ANY browser (phone, laptop, etc.):")
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "login",
         "--no-browser", "--format=json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"  ❌ Error: {result.stderr}")
        return False

    try:
        data = json.loads(result.stdout)
        print(f"\n  🔗 {data.get('verification_url', '')}")
        print(f"\n  🆔 Code: {data.get('user_code', '')}")
    except json.JSONDecodeError:
        print(f"  Output: {result.stdout}")
        print(f"  Stderr: {result.stderr}")
        print("\n  Run manually: gcloud auth application-default login --no-browser")

    print("\n  ⏳ Waiting for you to complete auth... (press Enter when done)")
    input()
    print("  ✅ gcloud auth configured!")
    return True


def setup_notebooklm():
    """Set up NotebookLM auth.

    Two approaches:
    1. xvfb-run (try this first — might work if DISPLAY available)
    2. Cookie import from exported auth file
    """
    print("\n📓 Setting up NotebookLM auth...")

    auth_dir = HOME / ".notebooklm" / "profiles" / "default"
    auth_file = auth_dir / "auth.json"
    auth_dir.mkdir(parents=True, exist_ok=True)

    if auth_file.exists():
        print("  ✅ NotebookLM already authenticated!")
        return True

    print("""
  ╔══════════════════════════════════════════════════════════════╗
  ║  Two ways to authenticate:                                  ║
  ║                                                              ║
  ║  A) Auto (try xvfb-run):                                    ║
  ║     xvfb-run notebooklm login --browser chromium            ║
  ║     (needs DISPLAY — may work on VPS with xvfb installed)    ║
  ║                                                              ║
  ║  B) From your laptop (RECOMMENDED):                         ║
  ║     1. On your laptop: notebooklm login --browser chromium  ║
  ║     2. scp ~/.notebooklm/profiles/default/auth.json \\       ║
  ║          ubuntu@149.56.46.173:~/.notebooklm/profiles/default/║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
    """)

    choice = input("Try auto-auth with xvfb? (y/n): ").strip().lower()
    if choice == "y":
        print("  Starting xvfb-run notebooklm login...")
        result = subprocess.run(
            ["xvfb-run", "notebooklm", "login", "--browser", "chromium"],
            capture_output=True, text=True, timeout=120,
        )
        print(f"  stdout: {result.stdout}")
        print(f"  stderr: {result.stderr}")
        if auth_file.exists():
            print("  ✅ NotebookLM authenticated via xvfb!")
            return True
        print("  ❌ Auto-auth failed. Use method B (laptop export).")

    print("""
  To auth from your laptop:
    pip install notebooklm-py
    notebooklm login --browser chromium
    scp ~/.notebooklm/profiles/default/auth.json \\
        ubuntu@149.56.46.173:~/.notebooklm/profiles/default/
    """)
    return False


def install_gcloud():
    """Install gcloud CLI."""
    print("\n📦 Installing gcloud CLI...")
    try:
        subprocess.run(["gcloud", "--version"],
                       capture_output=True, timeout=5)
        print("  ✅ gcloud already installed!")
        return True
    except FileNotFoundError:
        pass

    print("  Downloading gcloud SDK...")
    result = subprocess.run(
        ["curl", "-sSL", "https://sdk.cloud.google.com", "-o", "/tmp/gcloud-install.sh"],
        capture_output=True, timeout=30,
    )
    if result.returncode != 0:
        print("  ❌ Download failed. Install manually:")
        print("     curl https://sdk.cloud.google.com | bash")
        return False

    subprocess.run(["bash", "/tmp/gcloud-install.sh",
                    "--disable-prompts"], timeout=120)
    print("  ✅ gcloud installed! Restart your shell or run:")
    print("     source ~/.bashrc")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Sonora Digital Corp — Google Auth Setup",
    )
    parser.add_argument("--gemini-key", help="Set Gemini API key directly (no browser)")
    parser.add_argument("--gcloud", action="store_true", help="Authenticate with gcloud")
    parser.add_argument("--notebooklm", action="store_true",
                        help="Set up NotebookLM auth")
    parser.add_argument("--install-gcloud", action="store_true",
                        help="Install gcloud CLI")
    parser.add_argument("--all", action="store_true",
                        help="Run all available auth methods")
    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════╗
║  Google Auth Setup — Sonora Digital Corp      ║
║  Headless VPS compatible                       ║
╚═══════════════════════════════════════════════╝
""")

    if args.install_gcloud:
        install_gcloud()

    if args.gemini_key:
        setup_gemini_key(args.gemini_key)

    if args.gcloud:
        setup_gcloud()

    if args.notebooklm:
        setup_notebooklm()

    if args.all or len(sys.argv) == 1:
        print("\n🔄 Running all auth methods...")

        print("\n─── Gemini API Key ───")
        key = os.environ.get("GEMINI_API_KEY", "")
        existing = " (already set)" if key else ""
        print(f"  Current: {'✅' if key else '❌'}{existing}")
        key_input = input("  Enter Gemini key (or Enter to skip): ").strip()
        if key_input:
            setup_gemini_key(key_input)

        print("\n─── gcloud Auth ───")
        setup_gcloud()

        print("\n─── NotebookLM Auth ───")
        setup_notebooklm()

    print("\n✅ Auth setup complete!")
    print("   Run 'python3 -c \"from mcp import ClientSession; ...\"' to test.")


if __name__ == "__main__":
    main()
