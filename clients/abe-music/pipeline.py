#!/usr/bin/env python3
"""
ABE Music — Weekly Data Pipeline

Pulls artist streaming data from Spotify API and updates the JSON data store.
Run weekly via cron for auto-updating KPIs.

Requires Spotify API credentials (set in .env or environment):
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET

If credentials aren't set, falls back to reporting current data with age.
"""

import json
import os
import sys
import time
import logging
import requests
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / 'data' / 'abe-music.json'
ENV_PATH = BASE_DIR / '.env'
LOG_PATH = BASE_DIR / 'logs' / 'pipeline.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v
    return env
def get_spotify_token(client_id, client_secret):
    r = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'client_credentials'
    }, auth=(client_id, client_secret), timeout=10)
    r.raise_for_status()
    return r.json()['access_token']


def get_artist_data(token, artist_id):
    r = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}', headers={
        'Authorization': f'Bearer {token}'
    }, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    return {
        'monthly_listeners': data.get('followers', {}).get('total', 0),
        'popularity': data.get('popularity', 0),
        'genres': data.get('genres', []),
        'name': data.get('name', ''),
        'spotify_url': data.get('external_urls', {}).get('spotify', ''),
        'image': data.get('images', [{}])[0].get('url', '') if data.get('images') else '',
    }


def get_top_tracks(token, artist_id, market='US'):
    try:
        r = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={market}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return [{
            'name': t['name'],
            'popularity': t.get('popularity', 0),
            'album': t.get('album', {}).get('name', ''),
            'url': t.get('external_urls', {}).get('spotify', ''),
            'duration_ms': t.get('duration_ms', 0),
        } for t in data.get('tracks', [])[:5]]
    except Exception as e:
        log.warning(f"Failed to fetch top tracks for {artist_id}: {e}")
        return []


def fetch_with_retry(token, artist_id, retries=3):
    for attempt in range(retries):
        try:
            data = get_artist_data(token, artist_id)
            tracks = get_top_tracks(token, artist_id)
            return data, tracks
        except requests.exceptions.RequestException as e:
            log.warning(f"Attempt {attempt + 1}/{retries} failed for {artist_id}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return None, []

def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run():
    env = load_env()
    client_id = env.get('SPOTIFY_CLIENT_ID') or os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = env.get('SPOTIFY_CLIENT_SECRET') or os.environ.get('SPOTIFY_CLIENT_SECRET')

    data = load_data()
    artists = {k: v for k, v in data['artists'].items() if v.get('spotify_url')}

    if not artists:
        log.info("No artists with Spotify URLs found. Nothing to update.")
        return

    if client_id and client_secret:
        log.info("Spotify API credentials found. Pulling live data...")
        try:
            token = get_spotify_token(client_id, client_secret)
        except Exception as e:
            log.error(f"Failed to get Spotify token: {e}")
            return

        sync_time = datetime.now(timezone.utc).isoformat()
        synced_count = 0

        for artist_id, artist in artists.items():
            sid = artist['spotify_url'].rstrip('/').split('/')[-1]
            log.info(f"Fetching data for {artist['nombre']} (id={sid})...")
            try:
                spotify_data, top_tracks = fetch_with_retry(token, sid)
                if spotify_data:
                    data['artists'][artist_id]['monthly_listeners'] = spotify_data['monthly_listeners']
                    data['artists'][artist_id]['popularity'] = spotify_data['popularity']
                    data['artists'][artist_id]['genres'] = spotify_data['genres']
                    data['artists'][artist_id]['spotify_name'] = spotify_data['name']
                    data['artists'][artist_id]['spotify_image'] = spotify_data['image']
                    data['artists'][artist_id]['top_tracks'] = top_tracks
                    data['artists'][artist_id]['last_spotify_sync'] = sync_time
                    log.info(f"  → {spotify_data['monthly_listeners']} followers, popularity {spotify_data['popularity']}, {len(top_tracks)} top tracks")
                    synced_count += 1
                else:
                    log.warning(f"  → Artist ID {sid} not found on Spotify")
                time.sleep(0.5)
            except Exception as e:
                log.error(f"  → Failed: {e}")

        save_data(data)
        log.info(f"Pipeline complete. Synced {synced_count}/{len(artists)} artists. Data saved.")
    else:
        log.info("No Spotify credentials. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")

    # Print current state
    total_streams = sum(a['streams'] for a in data['artists'].values())
    total_revenue = sum(a['revenue'] for a in data['artists'].values())
    log.info(f"Current totals: {total_streams:,} streams, ${total_revenue:,.2f} revenue")

if __name__ == '__main__':
    log.info("=== Pipeline Start ===")
    run()
    log.info("=== Pipeline End ===")
