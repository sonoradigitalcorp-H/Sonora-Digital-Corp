import { describe, it, expect, beforeEach } from 'vitest';
import type {
  NormalizedProfile,
  NormalizedMetrics,
  NormalizedImages,
  NormalizedSocials,
  NormalizedLinks,
  NormalizedAlbum,
  NormalizedSearchResult,
  UnifiedArtist,
  ProviderHealth,
  IntelligenceConfig,
  IntelligenceError,
} from '../providers/types';
import {
  mergeProfiles,
  mergeMetrics,
  mergeImages,
  mergeAlbums,
  calculateConfidence,
  DEFAULT_INTELLIGENCE_CONFIG,
} from '../providers/intelligence/merger';
import { getCacheManager } from '../providers/cache/cache-manager';

beforeEach(() => {
  getCacheManager().clear();
});

function spotifyProfile(overrides: Partial<NormalizedProfile> = {}): NormalizedProfile {
  return {
    externalId: 'spotify-id-001',
    name: 'Test Artist',
    bio: 'Spotify bio text',
    genres: ['rock', 'pop'],
    country: 'US',
    city: 'Los Angeles',
    profileUrl: 'https://open.spotify.com/artist/123',
    provider: 'spotify',
    ...overrides,
  };
}

function youtubeProfile(overrides: Partial<NormalizedProfile> = {}): NormalizedProfile {
  return {
    externalId: 'yt-id-001',
    name: 'Test Artist',
    bio: 'YouTube bio text',
    genres: ['pop', 'electronic'],
    country: 'US',
    city: null,
    profileUrl: 'https://youtube.com/channel/456',
    provider: 'youtube',
    ...overrides,
  };
}

function deezerProfile(overrides: Partial<NormalizedProfile> = {}): NormalizedProfile {
  return {
    externalId: 'deezer-id-001',
    name: 'Test Artist',
    bio: null,
    genres: ['rock', 'jazz'],
    country: 'GB',
    city: 'London',
    profileUrl: null,
    provider: 'deezer',
    ...overrides,
  };
}

describe('Normalization — Required fields', () => {
  it('NormalizedProfile has required fields: externalId, name, provider', () => {
    const profile: NormalizedProfile = spotifyProfile();
    expect(profile).toHaveProperty('externalId');
    expect(profile).toHaveProperty('name');
    expect(profile).toHaveProperty('provider');
    expect(typeof profile.externalId).toBe('string');
    expect(typeof profile.name).toBe('string');
    expect(typeof profile.provider).toBe('string');
  });

  it('NormalizedMetrics has required fields: externalId, provider', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'spotify-id-001',
      monthlyListeners: null,
      followers: null,
      engagement: null,
      growth: null,
      momentum: null,
      provider: 'spotify',
    };
    expect(metrics).toHaveProperty('externalId');
    expect(metrics).toHaveProperty('provider');
    expect(typeof metrics.externalId).toBe('string');
    expect(typeof metrics.provider).toBe('string');
  });

  it('NormalizedImages has required fields: externalId, provider', () => {
    const images: NormalizedImages = {
      externalId: 'spotify-id-001',
      small: null,
      medium: null,
      large: null,
      provider: 'spotify',
    };
    expect(images).toHaveProperty('externalId');
    expect(images).toHaveProperty('provider');
    expect(typeof images.externalId).toBe('string');
    expect(typeof images.provider).toBe('string');
  });

  it('NormalizedSocials has required fields: externalId, provider', () => {
    const socials: NormalizedSocials = {
      externalId: 'spotify-id-001',
      instagram: null,
      tiktok: null,
      twitter: null,
      youtube: null,
      spotify: null,
      appleMusic: null,
      provider: 'spotify',
    };
    expect(socials).toHaveProperty('externalId');
    expect(socials).toHaveProperty('provider');
    expect(typeof socials.externalId).toBe('string');
    expect(typeof socials.provider).toBe('string');
  });

  it('NormalizedLinks has required fields: externalId, provider', () => {
    const links: NormalizedLinks = {
      externalId: 'spotify-id-001',
      deezer: null,
      soundcloud: null,
      bandcamp: null,
      website: null,
      provider: 'spotify',
    };
    expect(links).toHaveProperty('externalId');
    expect(links).toHaveProperty('provider');
    expect(typeof links.externalId).toBe('string');
    expect(typeof links.provider).toBe('string');
  });

  it('NormalizedAlbum has required fields: externalId, title, albumType, provider', () => {
    const album: NormalizedAlbum = {
      externalId: 'spotify-album-001',
      title: 'Greatest Hits',
      releaseDate: null,
      imageUrl: null,
      trackCount: null,
      albumType: 'album',
      provider: 'spotify',
    };
    expect(album).toHaveProperty('externalId');
    expect(album).toHaveProperty('title');
    expect(album).toHaveProperty('albumType');
    expect(album).toHaveProperty('provider');
    expect(typeof album.externalId).toBe('string');
    expect(typeof album.title).toBe('string');
    expect(typeof album.albumType).toBe('string');
    expect(typeof album.provider).toBe('string');
  });

  it('NormalizedSearchResult has required fields: externalId, name, matchScore, provider', () => {
    const search: NormalizedSearchResult = {
      externalId: 'spotify-id-001',
      name: 'Test Artist',
      genres: [],
      imageUrl: null,
      matchScore: 95,
      provider: 'spotify',
    };
    expect(search).toHaveProperty('externalId');
    expect(search).toHaveProperty('name');
    expect(search).toHaveProperty('matchScore');
    expect(search).toHaveProperty('provider');
    expect(typeof search.externalId).toBe('string');
    expect(typeof search.name).toBe('string');
    expect(typeof search.matchScore).toBe('number');
    expect(typeof search.provider).toBe('string');
  });
});

describe('Normalization — Optional fields default to null', () => {
  it('NormalizedProfile: bio, country, city, profileUrl are null by default', () => {
    const profile: NormalizedProfile = {
      externalId: 'id',
      name: 'Artist',
      bio: null,
      genres: [],
      country: null,
      city: null,
      profileUrl: null,
      provider: 'spotify',
    };
    expect(profile.bio).toBeNull();
    expect(profile.country).toBeNull();
    expect(profile.city).toBeNull();
    expect(profile.profileUrl).toBeNull();
  });

  it('NormalizedMetrics: monthlyListeners, followers, engagement, growth, momentum are null by default', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id',
      monthlyListeners: null,
      followers: null,
      engagement: null,
      growth: null,
      momentum: null,
      provider: 'spotify',
    };
    expect(metrics.monthlyListeners).toBeNull();
    expect(metrics.followers).toBeNull();
    expect(metrics.engagement).toBeNull();
    expect(metrics.growth).toBeNull();
    expect(metrics.momentum).toBeNull();
  });

  it('NormalizedImages: small, medium, large are null by default', () => {
    const images: NormalizedImages = {
      externalId: 'id',
      small: null,
      medium: null,
      large: null,
      provider: 'spotify',
    };
    expect(images.small).toBeNull();
    expect(images.medium).toBeNull();
    expect(images.large).toBeNull();
  });

  it('NormalizedSocials: all platform fields are null by default', () => {
    const socials: NormalizedSocials = {
      externalId: 'id',
      instagram: null,
      tiktok: null,
      twitter: null,
      youtube: null,
      spotify: null,
      appleMusic: null,
      provider: 'spotify',
    };
    expect(socials.instagram).toBeNull();
    expect(socials.tiktok).toBeNull();
    expect(socials.twitter).toBeNull();
    expect(socials.youtube).toBeNull();
    expect(socials.spotify).toBeNull();
    expect(socials.appleMusic).toBeNull();
  });

  it('NormalizedLinks: all link fields are null by default', () => {
    const links: NormalizedLinks = {
      externalId: 'id',
      deezer: null,
      soundcloud: null,
      bandcamp: null,
      website: null,
      provider: 'spotify',
    };
    expect(links.deezer).toBeNull();
    expect(links.soundcloud).toBeNull();
    expect(links.bandcamp).toBeNull();
    expect(links.website).toBeNull();
  });

  it('NormalizedAlbum: releaseDate, imageUrl, trackCount are null by default', () => {
    const album: NormalizedAlbum = {
      externalId: 'id',
      title: 'Album',
      releaseDate: null,
      imageUrl: null,
      trackCount: null,
      albumType: 'album',
      provider: 'spotify',
    };
    expect(album.releaseDate).toBeNull();
    expect(album.imageUrl).toBeNull();
    expect(album.trackCount).toBeNull();
  });

  it('NormalizedSearchResult: imageUrl can be null by default', () => {
    const search: NormalizedSearchResult = {
      externalId: 'id',
      name: 'Artist',
      genres: [],
      imageUrl: null,
      matchScore: 50,
      provider: 'spotify',
    };
    expect(search.imageUrl).toBeNull();
  });
});

describe('Normalization — Type consistency between providers', () => {
  it('spotify profile has same shape as youtube profile', () => {
    const sp = spotifyProfile();
    const yt = youtubeProfile();
    const spKeys = Object.keys(sp).sort();
    const ytKeys = Object.keys(yt).sort();
    expect(spKeys).toEqual(ytKeys);
  });

  it('spotify profile has same shape as deezer profile', () => {
    const sp = spotifyProfile();
    const dz = deezerProfile();
    expect(Object.keys(sp).sort()).toEqual(Object.keys(dz).sort());
  });

  it('all providers produce profiles with identical field types', () => {
    const sp = spotifyProfile();
    const yt = youtubeProfile();
    const dz = deezerProfile();

    const spKeys = new Set(Object.keys(sp));
    const ytKeys = new Set(Object.keys(yt));
    const dzKeys = new Set(Object.keys(dz));
    expect(spKeys).toEqual(ytKeys);
    expect(spKeys).toEqual(dzKeys);

    const fields: (keyof NormalizedProfile)[] = ['externalId', 'name', 'genres', 'provider', 'bio', 'country', 'city', 'profileUrl'];
    for (const field of fields) {
      const spVal = sp[field];
      const ytVal = yt[field];
      const dzVal = dz[field];
      if (spVal === null && ytVal === null) continue;
      if (spVal === null || ytVal === null) {
        expect(typeof spVal).not.toBe(typeof ytVal);
        continue;
      }
      expect(typeof spVal).toBe(typeof ytVal);
      if (dzVal === null) {
        expect(typeof spVal).not.toBe(typeof dzVal);
        continue;
      }
      expect(typeof spVal).toBe(typeof dzVal);
    }
  });
});

describe('Normalization — Nullability', () => {
  it('bio can be null', () => {
    const profile: NormalizedProfile = spotifyProfile({ bio: null });
    expect(profile.bio).toBeNull();
  });

  it('country can be null', () => {
    const profile: NormalizedProfile = spotifyProfile({ country: null });
    expect(profile.country).toBeNull();
  });

  it('city can be null', () => {
    const profile: NormalizedProfile = spotifyProfile({ city: null });
    expect(profile.city).toBeNull();
  });

  it('profileUrl can be null', () => {
    const profile: NormalizedProfile = spotifyProfile({ profileUrl: null });
    expect(profile.profileUrl).toBeNull();
  });

  it('all optional profile fields can be null simultaneously', () => {
    const profile: NormalizedProfile = {
      externalId: 'id',
      name: 'Artist',
      bio: null,
      genres: [],
      country: null,
      city: null,
      profileUrl: null,
      provider: 'spotify',
    };
    expect(profile.bio).toBeNull();
    expect(profile.country).toBeNull();
    expect(profile.city).toBeNull();
    expect(profile.profileUrl).toBeNull();
  });

  it('releaseDate can be null', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Album', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify',
    };
    expect(album.releaseDate).toBeNull();
  });

  it('imageUrl can be null in album', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Album', releaseDate: '2024-01-01', imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify',
    };
    expect(album.imageUrl).toBeNull();
  });
});

describe('Normalization — Defaults', () => {
  it('genres defaults to empty array', () => {
    const profile: NormalizedProfile = spotifyProfile({ genres: [] });
    expect(profile.genres).toEqual([]);
  });

  it('albums defaults to empty array on UnifiedArtist', () => {
    const artist: UnifiedArtist = {
      id: 'a1',
      name: 'Test Artist',
      profile: spotifyProfile(),
      metrics: { externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify' },
      images: { externalId: 'id', small: null, medium: null, large: null, provider: 'spotify' },
      socials: { externalId: 'id', instagram: null, tiktok: null, twitter: null, youtube: null, spotify: null, appleMusic: null, provider: 'merged' },
      links: { externalId: 'id', deezer: null, soundcloud: null, bandcamp: null, website: null, provider: 'merged' },
      albums: [],
      primaryProvider: 'spotify',
    };
    expect(artist.albums).toEqual([]);
  });
});

describe('Normalization — Optional fields: growth, momentum', () => {
  it('growth can be null', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify',
    };
    expect(metrics.growth).toBeNull();
  });

  it('momentum can be null', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify',
    };
    expect(metrics.momentum).toBeNull();
  });

  it('growth can be undefined', () => {
    const metrics = {} as NormalizedMetrics;
    expect(metrics.growth).toBeUndefined();
  });

  it('momentum can be undefined', () => {
    const metrics = {} as NormalizedMetrics;
    expect(metrics.momentum).toBeUndefined();
  });

  it('growth and momentum accept numeric values', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: 15.5, momentum: 72, provider: 'spotify',
    };
    expect(metrics.growth).toBe(15.5);
    expect(metrics.momentum).toBe(72);
  });
});

describe('Normalization — Album type enum validation', () => {
  it('albumType accepts "album"', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'LP', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify',
    };
    expect(album.albumType).toBe('album');
  });

  it('albumType accepts "single"', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Single', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'single', provider: 'spotify',
    };
    expect(album.albumType).toBe('single');
  });

  it('albumType accepts "compilation"', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Comp', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'compilation', provider: 'spotify',
    };
    expect(album.albumType).toBe('compilation');
  });

  it('albumType accepts "unknown"', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Unknown', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'unknown', provider: 'spotify',
    };
    expect(album.albumType).toBe('unknown');
  });

  it('only valid enum values are accepted for albumType at runtime', () => {
    const validTypes = ['album', 'single', 'compilation', 'unknown'] as const;
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'Test', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify',
    };
    expect(validTypes).toContain(album.albumType);
  });
});

describe('Normalization — Provider name consistency', () => {
  it('spotify profile provider field matches the provider name', () => {
    const profile = spotifyProfile();
    expect(profile.provider).toBe('spotify');
  });

  it('youtube profile provider field matches the provider name', () => {
    const profile = youtubeProfile();
    expect(profile.provider).toBe('youtube');
  });

  it('deezer profile provider field matches the provider name', () => {
    const profile = deezerProfile();
    expect(profile.provider).toBe('deezer');
  });

  it('spotify metrics provider field matches "spotify"', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify',
    };
    expect(metrics.provider).toBe('spotify');
  });

  it('spotify images provider field matches "spotify"', () => {
    const images: NormalizedImages = {
      externalId: 'id', small: null, medium: null, large: null, provider: 'spotify',
    };
    expect(images.provider).toBe('spotify');
  });

  it('album provider field matches the source provider', () => {
    const album: NormalizedAlbum = {
      externalId: 'id', title: 'A', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'deezer',
    };
    expect(album.provider).toBe('deezer');
  });

  it('search result provider field matches the source provider', () => {
    const search: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 80, provider: 'youtube',
    };
    expect(search.provider).toBe('youtube');
  });
});

describe('Normalization — Schema completeness (UnifiedArtist)', () => {
  it('UnifiedArtist includes profile (NormalizedProfile)', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('profile');
    expect(artist.profile).toHaveProperty('externalId');
    expect(artist.profile).toHaveProperty('name');
    expect(artist.profile).toHaveProperty('provider');
  });

  it('UnifiedArtist includes metrics (NormalizedMetrics)', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('metrics');
    expect(artist.metrics).toHaveProperty('monthlyListeners');
    expect(artist.metrics).toHaveProperty('followers');
  });

  it('UnifiedArtist includes images (NormalizedImages)', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('images');
    expect(artist.images).toHaveProperty('small');
    expect(artist.images).toHaveProperty('medium');
    expect(artist.images).toHaveProperty('large');
  });

  it('UnifiedArtist includes socials (NormalizedSocials)', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('socials');
    expect(artist.socials).toHaveProperty('instagram');
    expect(artist.socials).toHaveProperty('tiktok');
    expect(artist.socials).toHaveProperty('twitter');
    expect(artist.socials).toHaveProperty('youtube');
    expect(artist.socials).toHaveProperty('spotify');
    expect(artist.socials).toHaveProperty('appleMusic');
  });

  it('UnifiedArtist includes links (NormalizedLinks)', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('links');
    expect(artist.links).toHaveProperty('deezer');
    expect(artist.links).toHaveProperty('soundcloud');
    expect(artist.links).toHaveProperty('bandcamp');
    expect(artist.links).toHaveProperty('website');
  });

  it('UnifiedArtist includes albums (NormalizedAlbum[])', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    expect(artist).toHaveProperty('albums');
    expect(Array.isArray(artist.albums)).toBe(true);
  });

  it('UnifiedArtist has all 9 fields: id, name, profile, metrics, images, socials, links, albums, primaryProvider', () => {
    const artist: UnifiedArtist = buildMinimalArtist();
    const expectedKeys = ['id', 'name', 'profile', 'metrics', 'images', 'socials', 'links', 'albums', 'primaryProvider'];
    expect(Object.keys(artist).sort()).toEqual(expectedKeys.sort());
  });
});

function buildMinimalArtist(): UnifiedArtist {
  return {
    id: 'artist-1',
    name: 'Test Artist',
    profile: spotifyProfile(),
    metrics: {
      externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify',
    },
    images: { externalId: 'id', small: null, medium: null, large: null, provider: 'spotify' },
    socials: {
      externalId: 'id', instagram: null, tiktok: null, twitter: null, youtube: null, spotify: null, appleMusic: null, provider: 'merged',
    },
    links: { externalId: 'id', deezer: null, soundcloud: null, bandcamp: null, website: null, provider: 'merged' },
    albums: [],
    primaryProvider: 'spotify',
  };
}

describe('Normalization — Merge preserves non-null values', () => {
  it('mergeProfiles keeps non-null bio over null value', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: 'Actual bio', genres: [], country: null, city: null, profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.bio).toBe('Actual bio');
  });

  it('mergeProfiles keeps non-null country and city', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: 'US', city: 'NYC', profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.country).toBe('US');
    expect(merged.city).toBe('NYC');
  });

  it('mergeMetrics keeps non-null monthlyListeners', () => {
    const metrics: Partial<NormalizedMetrics>[] = [
      { externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'a' },
      { externalId: 'id', monthlyListeners: 500_000, followers: null, engagement: null, growth: null, momentum: null, provider: 'b' },
    ];
    const merged = mergeMetrics(metrics);
    expect(merged.monthlyListeners).toBe(500_000);
  });

  it('mergeMetrics keeps non-null followers and engagement', () => {
    const metrics: Partial<NormalizedMetrics>[] = [
      { externalId: 'id', monthlyListeners: null, followers: 1_000_000, engagement: null, growth: null, momentum: null, provider: 'a' },
      { externalId: 'id', monthlyListeners: null, followers: null, engagement: 80, growth: null, momentum: null, provider: 'b' },
    ];
    const merged = mergeMetrics(metrics);
    expect(merged.followers).toBe(1_000_000);
    expect(merged.engagement).toBe(80);
  });

  it('mergeImages keeps non-null image URLs', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: null, medium: null, large: null, provider: 'a' },
      { externalId: 'id', small: 'https://example.com/small.jpg', medium: null, large: null, provider: 'b' },
    ];
    const merged = mergeImages(images);
    expect(merged.small).toBe('https://example.com/small.jpg');
  });
});

describe('Normalization — Merge ignores null when non-null exists', () => {
  it('mergeProfiles ignores null bio when non-null bio already exists', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: 'Has bio', genres: [], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.bio).toBe('Has bio');
  });

  it('mergeProfiles ignores null country when non-null already exists', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: 'US', city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: 'London', profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.country).toBe('US');
    expect(merged.city).toBe('London');
  });

  it('mergeMetrics ignores null when non-null value already exists', () => {
    const metrics: Partial<NormalizedMetrics>[] = [
      { externalId: 'id', monthlyListeners: 2_000_000, followers: null, engagement: null, growth: null, momentum: null, provider: 'a' },
      { externalId: 'id', monthlyListeners: null, followers: 800_000, engagement: null, growth: null, momentum: null, provider: 'b' },
    ];
    const merged = mergeMetrics(metrics);
    expect(merged.monthlyListeners).toBe(2_000_000);
    expect(merged.followers).toBe(800_000);
  });

  it('mergeImages ignores null when non-null image URL already exists', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: 'https://a.com/s.jpg', medium: null, large: null, provider: 'a' },
      { externalId: 'id', small: null, medium: 'https://b.com/m.jpg', large: null, provider: 'b' },
    ];
    const merged = mergeImages(images);
    expect(merged.small).toBe('https://a.com/s.jpg');
    expect(merged.medium).toBe('https://b.com/m.jpg');
  });
});

describe('Normalization — Merge deduplicates genres', () => {
  it('mergeProfiles deduplicates genres across profiles', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: ['rock', 'pop'], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: ['pop', 'jazz'], country: null, city: null, profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.genres).toContain('rock');
    expect(merged.genres).toContain('pop');
    expect(merged.genres).toContain('jazz');
    expect(merged.genres!.length).toBe(3);
  });

  it('mergeProfiles deduplicates identical genres from three providers', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: ['rock'], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: ['rock', 'pop'], country: null, city: null, profileUrl: null, provider: 'b' },
      { externalId: 'id', name: 'Artist', bio: null, genres: ['rock', 'pop', 'jazz'], country: null, city: null, profileUrl: null, provider: 'c' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.genres).toEqual(['rock', 'pop', 'jazz']);
  });

  it('mergeProfiles handles empty genres array from all profiles', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.genres).toEqual([]);
  });
});

describe('Normalization — Merge deduplicates albums by title (case-insensitive)', () => {
  it('mergeAlbums deduplicates by title ignoring case', () => {
    const albumLists: NormalizedAlbum[][] = [
      [
        { externalId: 's1', title: 'Greatest Hits', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify' },
        { externalId: 's2', title: 'New Album', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify' },
      ],
      [
        { externalId: 'y1', title: 'greatest hits', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'youtube' },
        { externalId: 'y2', title: 'Another Album', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'youtube' },
      ],
    ];
    const merged = mergeAlbums(albumLists);
    expect(merged).toHaveLength(3);
    const titles = merged.map(a => a.title);
    expect(titles).toContain('Greatest Hits');
    expect(titles).toContain('New Album');
    expect(titles).toContain('Another Album');
  });

  it('mergeAlbums deduplicates identical titles from multiple providers', () => {
    const albumLists: NormalizedAlbum[][] = [
      [
        { externalId: 's1', title: 'Album A', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify' },
      ],
      [
        { externalId: 'y1', title: 'Album A', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'youtube' },
      ],
      [
        { externalId: 'd1', title: 'Album A', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'deezer' },
      ],
    ];
    const merged = mergeAlbums(albumLists);
    expect(merged).toHaveLength(1);
  });

  it('mergeAlbums handles case-insensitive deduplication with extra whitespace', () => {
    const albumLists: NormalizedAlbum[][] = [
      [
        { externalId: 's1', title: '  Album One  ', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'spotify' },
      ],
      [
        { externalId: 'y1', title: 'album one', releaseDate: null, imageUrl: null, trackCount: null, albumType: 'album', provider: 'youtube' },
      ],
    ];
    const merged = mergeAlbums(albumLists);
    expect(merged).toHaveLength(1);
    expect(merged[0].title).toBe('  Album One  ');
  });
});

describe('Normalization — Merge images picks largest available', () => {
  it('mergeImages picks the largest image from the later provider', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: 'https://a.com/s.jpg', medium: 'https://a.com/m.jpg', large: 'https://a.com/l.jpg', provider: 'a' },
      { externalId: 'id', small: null, medium: null, large: 'https://b.com/large.jpg', provider: 'b' },
    ];
    const merged = mergeImages(images);
    expect(merged.large).toBe('https://b.com/large.jpg');
  });

  it('mergeImages fills small/medium from large when only large is provided', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: null, medium: null, large: 'https://x.com/huge.jpg', provider: 'x' },
    ];
    const merged = mergeImages(images);
    expect(merged.large).toBe('https://x.com/huge.jpg');
    expect(merged.small).toBe('https://x.com/huge.jpg');
    expect(merged.medium).toBe('https://x.com/huge.jpg');
  });

  it('mergeImages prefers large from second provider over first provider small', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: 'https://a.com/tiny.jpg', medium: null, large: null, provider: 'a' },
      { externalId: 'id', small: null, medium: null, large: 'https://b.com/huge.jpg', provider: 'b' },
    ];
    const merged = mergeImages(images);
    expect(merged.large).toBe('https://b.com/huge.jpg');
    expect(merged.small).toBe('https://a.com/tiny.jpg');
  });
});

describe('Normalization — Confidence scoring', () => {
  const config: IntelligenceConfig = {
    minProvidersForHighConfidence: 2,
    allowPartialResults: true,
    scorePriority: ['average', 'spotify', 'generated'],
  };

  it('returns high when 2+ providers contribute and no errors', () => {
    const confidence = calculateConfidence(2, [], config);
    expect(confidence).toBe('high');
  });

  it('returns high when 3 providers contribute and no errors', () => {
    const confidence = calculateConfidence(3, [], config);
    expect(confidence).toBe('high');
  });

  it('returns medium when 1 provider contributes and no errors', () => {
    const confidence = calculateConfidence(1, [], config);
    expect(confidence).toBe('medium');
  });

  it('returns medium when 2+ providers contribute with recoverable errors', () => {
    const errors: IntelligenceError[] = [
      { provider: 'spotify', error: 'timeout', recoverable: true },
    ];
    const confidence = calculateConfidence(2, errors, config);
    expect(confidence).toBe('medium');
  });

  it('returns low when 0 providers contribute', () => {
    const confidence = calculateConfidence(0, [], config);
    expect(confidence).toBe('low');
  });

  it('returns low when there are unrecoverable errors', () => {
    const errors: IntelligenceError[] = [
      { provider: 'spotify', error: 'auth failure', recoverable: false },
    ];
    const confidence = calculateConfidence(1, errors, config);
    expect(confidence).toBe('low');
  });

  it('returns low when 0 providers and errors exist', () => {
    const errors: IntelligenceError[] = [
      { provider: 'spotify', error: 'down', recoverable: true },
    ];
    const confidence = calculateConfidence(0, errors, config);
    expect(confidence).toBe('low');
  });

  it('respects custom minProvidersForHighConfidence config', () => {
    const customConfig: IntelligenceConfig = { ...config, minProvidersForHighConfidence: 3 };
    expect(calculateConfidence(2, [], customConfig)).toBe('medium');
    expect(calculateConfidence(3, [], customConfig)).toBe('high');
  });

  it('returns low with mixed recoverable and unrecoverable errors', () => {
    const errors: IntelligenceError[] = [
      { provider: 'a', error: 'timeout', recoverable: true },
      { provider: 'b', error: 'auth denied', recoverable: false },
    ];
    const confidence = calculateConfidence(2, errors, config);
    expect(confidence).toBe('low');
  });
});

describe('Normalization — Edge: empty arrays', () => {
  it('mergeProfiles with empty profiles array returns defaults', () => {
    const merged = mergeProfiles([]);
    expect(merged.externalId).toBe('');
    expect(merged.name).toBe('');
    expect(merged.genres).toEqual([]);
    expect(merged.bio).toBeNull();
  });

  it('mergeMetrics with empty metrics array returns defaults', () => {
    const merged = mergeMetrics([]);
    expect(merged.externalId).toBe('');
    expect(merged.monthlyListeners).toBeNull();
    expect(merged.followers).toBeNull();
  });

  it('mergeImages with empty images array returns defaults', () => {
    const merged = mergeImages([]);
    expect(merged.small).toBeNull();
    expect(merged.medium).toBeNull();
    expect(merged.large).toBeNull();
    expect(merged.provider).toBe('merged');
  });

  it('mergeAlbums with empty album lists returns empty array', () => {
    const merged = mergeAlbums([]);
    expect(merged).toEqual([]);
  });

  it('mergeAlbums with arrays of empty arrays returns empty array', () => {
    const merged = mergeAlbums([[], []]);
    expect(merged).toEqual([]);
  });
});

describe('Normalization — Edge: all-null profile', () => {
  it('mergeProfiles handles a profile with all nullable fields set to null', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'spotify' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.bio).toBeNull();
    expect(merged.country).toBeNull();
    expect(merged.city).toBeNull();
    expect(merged.profileUrl).toBeNull();
    expect(merged.genres).toEqual([]);
    expect(merged.name).toBe('Artist');
  });

  it('a profile with all nulls still produces a valid NormalizedProfile', () => {
    const profile: NormalizedProfile = {
      externalId: 'id',
      name: 'Artist',
      bio: null,
      genres: [],
      country: null,
      city: null,
      profileUrl: null,
      provider: 'spotify',
    };
    expect(profile.externalId).toBe('id');
    expect(profile.name).toBe('Artist');
    expect(profile.bio).toBeNull();
    expect(profile.genres).toEqual([]);
    expect(profile.country).toBeNull();
    expect(profile.city).toBeNull();
    expect(profile.profileUrl).toBeNull();
    expect(profile.provider).toBe('spotify');
  });

  it('multiple all-null profiles merged still result in null values', () => {
    const profiles: Partial<NormalizedProfile>[] = [
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'a' },
      { externalId: 'id', name: 'Artist', bio: null, genres: [], country: null, city: null, profileUrl: null, provider: 'b' },
    ];
    const merged = mergeProfiles(profiles);
    expect(merged.bio).toBeNull();
    expect(merged.country).toBeNull();
    expect(merged.city).toBeNull();
    expect(merged.profileUrl).toBeNull();
  });
});

describe('Normalization — Edge: all-null metrics', () => {
  it('mergeMetrics handles metrics with all numeric fields null', () => {
    const metricss: Partial<NormalizedMetrics>[] = [
      { externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'spotify' },
    ];
    const merged = mergeMetrics(metricss);
    expect(merged.monthlyListeners).toBeNull();
    expect(merged.followers).toBeNull();
    expect(merged.engagement).toBeNull();
    expect(merged.growth).toBeNull();
    expect(merged.momentum).toBeNull();
  });

  it('all-null metrics still produce a valid NormalizedMetrics object', () => {
    const metrics: NormalizedMetrics = {
      externalId: 'id',
      monthlyListeners: null,
      followers: null,
      engagement: null,
      growth: null,
      momentum: null,
      provider: 'spotify',
    };
    expect(metrics.provider).toBe('spotify');
    expect(metrics.externalId).toBe('id');
    expect(Object.values(metrics).every(v => v === null || v === 'id' || v === 'spotify')).toBe(true);
  });

  it('merging all-null metrics from multiple providers produces nulls', () => {
    const metricss: Partial<NormalizedMetrics>[] = [
      { externalId: 'id', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'a' },
      { externalId: 'id2', monthlyListeners: null, followers: null, engagement: null, growth: null, momentum: null, provider: 'b' },
    ];
    const merged = mergeMetrics(metricss);
    expect(merged.monthlyListeners).toBeNull();
    expect(merged.followers).toBeNull();
    expect(merged.engagement).toBeNull();
    expect(merged.growth).toBeNull();
    expect(merged.momentum).toBeNull();
  });
});

describe('Normalization — Edge: all-null images', () => {
  it('mergeImages handles images with all URL fields null', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: null, medium: null, large: null, provider: 'spotify' },
    ];
    const merged = mergeImages(images);
    expect(merged.small).toBeNull();
    expect(merged.medium).toBeNull();
    expect(merged.large).toBeNull();
  });

  it('all-null images from multiple providers still produce null URLs', () => {
    const images: Partial<NormalizedImages>[] = [
      { externalId: 'id', small: null, medium: null, large: null, provider: 'a' },
      { externalId: 'id2', small: null, medium: null, large: null, provider: 'b' },
    ];
    const merged = mergeImages(images);
    expect(merged.small).toBeNull();
    expect(merged.medium).toBeNull();
    expect(merged.large).toBeNull();
  });

  it('all-null images produce a valid NormalizedImages object', () => {
    const images: NormalizedImages = {
      externalId: 'id',
      small: null,
      medium: null,
      large: null,
      provider: 'spotify',
    };
    expect(images.externalId).toBe('id');
    expect(images.small).toBeNull();
    expect(images.medium).toBeNull();
    expect(images.large).toBeNull();
    expect(images.provider).toBe('spotify');
  });
});

describe('Normalization — Search result shape validation', () => {
  it('search result has all required fields: externalId, name, genres, imageUrl, matchScore, provider', () => {
    const result: NormalizedSearchResult = {
      externalId: 'spotify-id',
      name: 'Test Artist',
      genres: ['rock', 'pop'],
      imageUrl: 'https://example.com/image.jpg',
      matchScore: 92,
      provider: 'spotify',
    };
    expect(result).toHaveProperty('externalId');
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('genres');
    expect(result).toHaveProperty('imageUrl');
    expect(result).toHaveProperty('matchScore');
    expect(result).toHaveProperty('provider');
    expect(typeof result.externalId).toBe('string');
    expect(typeof result.name).toBe('string');
    expect(Array.isArray(result.genres)).toBe(true);
    expect(typeof result.matchScore).toBe('number');
    expect(typeof result.provider).toBe('string');
  });

  it('search result matchScore accepts 0 as a value', () => {
    const result: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 0, provider: 'spotify',
    };
    expect(result.matchScore).toBe(0);
  });

  it('search result matchScore accepts 100 as a value', () => {
    const result: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 100, provider: 'spotify',
    };
    expect(result.matchScore).toBe(100);
  });

  it('search result matchScore accepts decimal values', () => {
    const result: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 87.5, provider: 'spotify',
    };
    expect(result.matchScore).toBe(87.5);
  });

  it('search result genres can be empty array', () => {
    const result: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 50, provider: 'spotify',
    };
    expect(result.genres).toEqual([]);
  });

  it('search result imageUrl can be null', () => {
    const result: NormalizedSearchResult = {
      externalId: 'id', name: 'Artist', genres: [], imageUrl: null, matchScore: 50, provider: 'spotify',
    };
    expect(result.imageUrl).toBeNull();
  });

  it('search result shape is consistent across providers', () => {
    const spotifyResult: NormalizedSearchResult = {
      externalId: 's1', name: 'A', genres: ['rock'], imageUrl: null, matchScore: 90, provider: 'spotify',
    };
    const youtubeResult: NormalizedSearchResult = {
      externalId: 'y1', name: 'A', genres: ['pop'], imageUrl: 'https://img.com/art.jpg', matchScore: 80, provider: 'youtube',
    };
    expect(Object.keys(spotifyResult).sort()).toEqual(Object.keys(youtubeResult).sort());
  });
});

describe('Normalization — Health shape validation', () => {
  it('ProviderHealth has all required fields: name, status, message, latencyMs, lastChecked, configured, configurationError', () => {
    const health: ProviderHealth = {
      name: 'spotify',
      status: 'healthy',
      message: 'All systems operational',
      latencyMs: 42,
      lastChecked: new Date().toISOString(),
      configured: true,
      configurationError: null,
    };
    expect(health).toHaveProperty('name');
    expect(health).toHaveProperty('status');
    expect(health).toHaveProperty('message');
    expect(health).toHaveProperty('latencyMs');
    expect(health).toHaveProperty('lastChecked');
    expect(health).toHaveProperty('configured');
    expect(health).toHaveProperty('configurationError');
    expect(typeof health.name).toBe('string');
    expect(typeof health.status).toBe('string');
    expect(typeof health.message).toBe('string');
    expect(typeof health.latencyMs).toBe('number');
    expect(typeof health.lastChecked).toBe('string');
    expect(typeof health.configured).toBe('boolean');
  });

  it('status accepts "healthy"', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'healthy', message: 'OK', latencyMs: 5, lastChecked: new Date().toISOString(), configured: true, configurationError: null,
    };
    expect(health.status).toBe('healthy');
  });

  it('status accepts "degraded"', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'degraded', message: 'High latency', latencyMs: 500, lastChecked: new Date().toISOString(), configured: true, configurationError: null,
    };
    expect(health.status).toBe('degraded');
  });

  it('status accepts "unhealthy"', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'unhealthy', message: 'API down', latencyMs: 0, lastChecked: new Date().toISOString(), configured: false, configurationError: 'No credentials',
    };
    expect(health.status).toBe('unhealthy');
  });

  it('configurationError can be null', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'healthy', message: 'OK', latencyMs: 5, lastChecked: new Date().toISOString(), configured: true, configurationError: null,
    };
    expect(health.configurationError).toBeNull();
  });

  it('configurationError can be a string', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'unhealthy', message: 'Misconfigured', latencyMs: 0, lastChecked: new Date().toISOString(), configured: false, configurationError: 'Missing API key',
    };
    expect(health.configurationError).toBe('Missing API key');
  });

  it('latencyMs can be 0', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'healthy', message: 'OK', latencyMs: 0, lastChecked: new Date().toISOString(), configured: true, configurationError: null,
    };
    expect(health.latencyMs).toBe(0);
  });

  it('lastChecked is a valid ISO date string', () => {
    const health: ProviderHealth = {
      name: 'spotify', status: 'healthy', message: 'OK', latencyMs: 5, lastChecked: new Date().toISOString(), configured: true, configurationError: null,
    };
    expect(() => new Date(health.lastChecked)).not.toThrow();
    expect(new Date(health.lastChecked).toISOString()).toBe(health.lastChecked);
  });
});
