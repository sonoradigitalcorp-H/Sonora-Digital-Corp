# SIGNAL Data Normalization Layer

> Every provider returns data mapped into one of these schemas.
> The Intelligence Engine assembles them into a unified Artist.

---

## Normalized Schemas

### NormalizedProfile

Core identity data that every artist has.

```typescript
interface NormalizedProfile {
  externalId: string;      // Provider-specific ID
  name: string;            // Artist display name
  bio: string | null;      // Biography
  genres: string[];        // Top 3-5 genres
  country: string | null;  // Country of origin
  city: string | null;     // City of origin
  profileUrl: string | null; // URL to profile on platform
  provider: string;        // Source provider name
}
```

**Provider mapping:**
| Field | Spotify | Deezer | Generated |
|-------|---------|--------|-----------|
| `externalId` | Spotify ID | Deezer ID | Artist pool ID |
| `name` | Artist name | Artist name | Pool name |
| `bio` | ❌ N/A | ❌ N/A | ✅ Context |
| `genres` | ✅ Genre tags | ❌ N/A | ✅ Pool genres |
| `country` | ❌ N/A | ❌ N/A | ✅ Pool country |
| `city` | ❌ N/A | ❌ N/A | ✅ Pool city |
| `profileUrl` | Spotify URL | Deezer URL | ❌ N/A |

---

### NormalizedMetrics

Audience and performance data.

```typescript
interface NormalizedMetrics {
  externalId: string;
  monthlyListeners: number | null;
  followers: number | null;
  engagement: number | null;    // 0-100
  growth: number | null;        // % over 30 days
  momentum: number | null;      // 0-100
  provider: string;
}
```

**Provider mapping:**
| Field | Spotify | Deezer | Generated |
|-------|---------|--------|-----------|
| `monthlyListeners` | ❌ Removed Feb 2026 | ❌ N/A | ✅ Generated |
| `followers` | ❌ Removed Feb 2026 | ❌ N/A | ✅ Generated |
| `engagement` | ❌ N/A | ❌ N/A | ✅ Generated |
| `growth` | ❌ N/A | ❌ N/A | ✅ Generated |
| `momentum` | ❌ N/A | ❌ N/A | ✅ Generated |

> **Note**: Since Spotify's Feb 2026 API changes removed `followers` and `popularity`, all metrics come from SIGNAL's generated data layer. This provides consistent, always-available metrics.

---

### NormalizedImages

Artist images at standard sizes.

```typescript
interface NormalizedImages {
  externalId: string;
  small: string | null;   // ≤ 160px
  medium: string | null;  // ~320px
  large: string | null;   // ≥ 640px
  provider: string;
}
```

**Provider mapping:**
| Field | Spotify | Deezer |
|-------|---------|--------|
| `small` | 3rd image | `picture_small` |
| `medium` | 2nd image | `picture_medium` |
| `large` | 1st image | `picture_big` or `picture_xl` |

**Resolution priority**: Spotify > Deezer > Generated fallback

---

### NormalizedSocials

Social media links.

```typescript
interface NormalizedSocials {
  externalId: string;
  instagram: string | null;
  tiktok: string | null;
  twitter: string | null;
  youtube: string | null;
  spotify: string | null;
  appleMusic: string | null;
  provider: string;
}
```

Currently populated from data-generator pool entries. Future providers (Instagram, TikTok) will enrich these fields.

---

### NormalizedLinks

External platform links.

```typescript
interface NormalizedLinks {
  externalId: string;
  deezer: string | null;
  soundcloud: string | null;
  bandcamp: string | null;
  website: string | null;
  provider: string;
}
```

---

### NormalizedAlbum

Album/discography entry.

```typescript
interface NormalizedAlbum {
  externalId: string;
  title: string;
  releaseDate: string | null;
  imageUrl: string | null;
  trackCount: number | null;
  albumType: 'album' | 'single' | 'compilation' | 'unknown';
  provider: string;
}
```

**Provider mapping:**
| Field | Spotify |
|-------|---------|
| `title` | Album name |
| `releaseDate` | `release_date` |
| `imageUrl` | Album cover |
| `trackCount` | `total_tracks` |
| `albumType` | `album_type` |

---

## Merge Logic

The Intelligence Engine's merger combines data from multiple providers:

### Profile Merge
- First non-null value wins
- Genres are **merged and deduplicated**
- Later providers override earlier ones for non-null values

### Metrics Merge
- First non-null value wins
- If Spotify returns null (Feb 2026), generated metrics fill the gap

### Image Merge
- Largest available image wins
- If Spotify has large but Deezer has better medium, Spotify large takes priority
- Missing sizes are filled from available ones

### Album Merge
- Deduplicated by lowercase title
- Spotify is primary source for albums

---

## UnifiedArtist (Final Output)

```typescript
interface UnifiedArtist {
  id: string;
  name: string;
  profile: NormalizedProfile;
  metrics: NormalizedMetrics;
  images: NormalizedImages;
  socials: NormalizedSocials;
  links: NormalizedLinks;
  albums: NormalizedAlbum[];
  primaryProvider: string; // Source that provided the artist name
}
```

Each `UnifiedArtist` also has a confidence score:
- **High**: ≥2 providers contributed, no errors
- **Medium**: ≥1 provider contributed, recoverable errors only
- **Low**: Only generated data available

---

## Adding a New Normalized Type

1. Define the interface in `providers/types.ts`
2. Add the field to `UnifiedArtist`
3. Create a merge function in `providers/intelligence/merger.ts`
4. Update the Intelligence Engine's `buildArtist()` method
5. Implement `fetch*()` on each provider
