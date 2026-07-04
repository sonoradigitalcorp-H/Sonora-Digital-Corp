// ───────────────────────────────────────────────
// SIGNAL Score Engine — Public API
// ───────────────────────────────────────────────

// Core types
export type {
  ArtistFeatures,
  WeightConfig,
  WeightOverrides,
  ScoreResult,
  ScoreReasoning,
  ScoreInputSpec,
  ValidationResult,
  ScoreHistory,
  ScoreHistoryEntry,
  ScoreIdentity,
  ScoreCategory,
  ScoreRegistration,
  ScoreRegistryState,
  ContributingFactor,
  TrendDirection,
} from './types';

// Feature extraction
export { extractFeatures, normalizeFeatures } from './feature-extractor';

// Weight configuration
export { setGlobalWeights, resetGlobalWeights, resolveWeights, getEffectiveWeight, enableMLWeights } from './weights';

// Confidence
export { calculateConfidence, computeFactorAgreement, estimateDataFreshness } from './confidence';

// Reasoning / explainability
export { buildReasoning, formatFactors, formatScoreForDisplay } from './reasoning';

// Base score
export { BaseScore, clamp, normalizeToRange, weightedImpact, weightedAverage, sigmoid } from './base-score';

// Registry
export { getRegistry, resetRegistry } from './score-registry';

// History
export { getHistoryManager, resetHistoryManager } from './score-history';

// Engine
export { getEngine, resetEngine } from './score-engine';
export type { ScoreOutput, EngineResult } from './score-engine';

// All score implementations
export { createDefaultScores } from './scores';
