from dataclasses import dataclass

SPLIT = {"artist": 0.70, "label": 0.20, "reserve": 0.10}
STREAMING_RATES = {"spotify": 0.004, "youtube": 0.002, "deezer": 0.003}


@dataclass
class ArtistRevenue:
    artist_id: str
    name: str
    streams: int
    platform: str
    revenue_bruto: float
    artist_share: float
    label_share: float
    reserve_share: float


def calculate_revenue(
    artist_id: str,
    name: str,
    streams: int,
    platform: str = "spotify",
) -> ArtistRevenue:
    rate = STREAMING_RATES.get(platform, 0.003)
    bruto = round(streams * rate, 2)
    return ArtistRevenue(
        artist_id=artist_id,
        name=name,
        streams=streams,
        platform=platform,
        revenue_bruto=bruto,
        artist_share=round(bruto * SPLIT["artist"], 2),
        label_share=round(bruto * SPLIT["label"], 2),
        reserve_share=round(bruto * SPLIT["reserve"], 2),
    )


def calculate_all_artists(artists_data: list[dict]) -> list[ArtistRevenue]:
    results = []
    for a in artists_data:
        rev = calculate_revenue(
            artist_id=a["id"],
            name=a["name"],
            streams=a.get("monthly_streams", 0),
        )
        results.append(rev)
    return results


def format_revenue_report(results: list[ArtistRevenue]) -> str:
    lines = ["📊 Reporte de Regalías", ""]
    total_label = 0.0
    for r in results:
        lines.append(f"{r.name}")
        lines.append(f"  Streams: {r.streams:,}")
        lines.append(f"  Revenue bruto: ${r.revenue_bruto:,.2f}")
        lines.append(f"  Split (70/20/10):")
        lines.append(f"    -> Artista: ${r.artist_share:,.2f}")
        lines.append(f"    -> Sello: ${r.label_share:,.2f}")
        lines.append(f"    -> Reserva: ${r.reserve_share:,.2f}")
        lines.append("")
        total_label += r.label_share
    lines.append(f"Total sello: ${total_label:,.2f}")
    return "\n".join(lines)
