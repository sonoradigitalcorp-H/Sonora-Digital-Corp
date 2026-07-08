// ───────────────────────────────────────────────
// SIGNAL Production-Readiness Test Configuration
// ───────────────────────────────────────────────

import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Environment
    environment: 'node',
    globals: true,
    setupFiles: ['./src/__tests__/setup.ts'],

    // Test discovery
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['node_modules', '.next'],

    // Coverage
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: [
        'src/providers/**/*.ts',
        'src/app/api/**/*.ts',
        'src/lib/**/*.ts',
        'src/scoring/**/*.ts',
      ],
      thresholds: {
        statements: 60,
        branches: 50,
        functions: 60,
        lines: 60,
      },
    },

    // Isolation
    testTransformMode: { web: ['**/*.tsx'] },
    sequence: {
      concurrent: true,
    },

    // Output (removed verbose — not supported in InlineConfig)
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
