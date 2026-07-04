// ───────────────────────────────────────────────
// SIGNAL Test Setup — Global Configuration
// ───────────────────────────────────────────────

import '@testing-library/jest-dom';

// ── Global Test Timeout ──

// Each provider test should complete within 10s
vi.setConfig({ testTimeout: 10000 });

// ── Clean Up Global Cache Between Tests ──

beforeEach(() => {
  // Clear global provider cache
  if (typeof globalThis.__providerCache !== 'undefined') {
    globalThis.__providerCache = new Map();
  }
  if (typeof globalThis.__cacheLastCleared !== 'undefined') {
    globalThis.__cacheLastCleared = Date.now();
  }

  // Clear environment-dependent module singletons
  // by clearing module registry cache
  vi.clearAllMocks();
});

afterEach(() => {
  // Ensure no dangling timeouts
  vi.restoreAllMocks();
  vi.useRealTimers();
});

// ── Declare Global Cache Type ──

declare global {
  // eslint-disable-next-line no-var
  var __providerCache: Map<string, unknown> | undefined;
  // eslint-disable-next-line no-var
  var __cacheLastCleared: number | undefined;
}

export {};
