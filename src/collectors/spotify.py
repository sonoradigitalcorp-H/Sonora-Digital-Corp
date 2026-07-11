import os
import httpx

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


async def get_artist_data(artist_spotify_id: str) -> dict | None:
    if not CLIENT_ID or not CLIENT_SECRET:
        return None
    async with httpx.AsyncClient() as client:
        auth = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
        if auth.status_code != 200:
            return None
        token = auth.json()["access_token"]
        res = await client.get(
            f"https://api.spotify.com/v1/artists/{artist_spotify_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if res.status_code != 200:
            return None
        data = res.json()
        return {
            "name": data["name"],
            "monthly_listeners": data["followers"]["total"],
            "genres": data["genres"],
            "popularity": data["popularity"],
            "image": data["images"][0]["url"] if data["images"] else None,
        }


async def get_artist_top_tracks(artist_spotify_id: str) -> list[dict]:
    if not CLIENT_ID or not CLIENT_SECRET:
        return []
    async with httpx.AsyncClient() as client:
        auth = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
        if auth.status_code != 200:
            return []
        token = auth.json()["access_token"]
        res = await client.get(
            f"https://api.spotify.com/v1/artists/{artist_spotify_id}/top-tracks?market=US",
            headers={"Authorization": f"Bearer {token}"},
        )
        if res.status_code != 200:
            return []
        tracks = res.json().get("tracks", [])
        return [
            {
                "name": t["name"],
                "popularity": t["popularity"],
                "url": t["external_urls"]["spotify"],
            }
            for t in tracks[:5]
        ]
