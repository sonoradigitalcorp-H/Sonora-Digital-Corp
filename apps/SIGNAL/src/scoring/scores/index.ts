// ───────────────────────────────────────────────
// SIGNAL Score Engine — Score Implementations
// Factory and re-exports
// ───────────────────────────────────────────────

import type { BaseScore } from '../base-score';
import { getRegistry } from '../score-registry';
import { MomentumScore } from './momentum-score';
import { GrowthVelocityScore } from './growth-velocity-score';
import { DiscoveryScore } from './discovery-score';
import { AudienceQualityScore } from './audience-quality-score';
import { ViralityIndex } from './virality-index';
import { LabelReadinessScore } from './label-readiness-score';
import { FanConversionScore } from './fan-conversion-score';
import { TourReadinessScore } from './tour-readiness-score';
import { BrandPartnershipScore } from './brand-partnership-score';
import { GlobalExpansionScore } from './global-expansion-score';

export { MomentumScore } from './momentum-score';
export { GrowthVelocityScore } from './growth-velocity-score';
export { DiscoveryScore } from './discovery-score';
export { AudienceQualityScore } from './audience-quality-score';
export { ViralityIndex } from './virality-index';
export { LabelReadinessScore } from './label-readiness-score';
export { FanConversionScore } from './fan-conversion-score';
export { TourReadinessScore } from './tour-readiness-score';
export { BrandPartnershipScore } from './brand-partnership-score';
export { GlobalExpansionScore } from './global-expansion-score';

/**
 * Create and register all default scores.
 * Returns the array of registered score instances.
 */
export async function createDefaultScores(): Promise<BaseScore[]> {
  const registry = getRegistry();
  const scores: BaseScore[] = [
    new MomentumScore(),
    new GrowthVelocityScore(),
    new DiscoveryScore(),
    new AudienceQualityScore(),
    new ViralityIndex(),
    new LabelReadinessScore(),
    new FanConversionScore(),
    new TourReadinessScore(),
    new BrandPartnershipScore(),
    new GlobalExpansionScore(),
  ];

  for (const score of scores) {
    await registry.register(score);
  }

  return scores;
}
