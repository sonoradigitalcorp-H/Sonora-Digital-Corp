# Search Knowledge — Core Capability Spec

**Version**: 1.0.0 | **Status**: active | **Owner**: null
**Business Domain**: system | **Cost Tier**: 1

## Description

Search across all memory stores (semantic, graph, long-term).

## Invariants

| ID | Rule | Critical |
|----|------|----------|
| INV-001 | Results MUST include source provenance | yes |
| INV-002 | Semantic search MUST return top-10 by cosine similarity | yes |
| INV-003 | Graph search MUST traverse max 3 hops | yes |

## Inputs

- Query string
- Optional: store filter, limit, threshold

## Outputs

- Ranked results with scores, sources, excerpts

## Events

None

## Success Criteria

| ID | Criterion | Measurable |
|----|-----------|------------|
| SC-001 | Query returns results within 2s | yes |
| SC-002 | Results include source metadata | yes |
| SC-003 | Empty query returns no results | yes |

## Dependencies

None

## Security Classification

internal

## LLM Fit

| Dimension | Value |
|-----------|-------|
| Complexity | low |
| Reasoning Level | low |
| Domain Specialization | general |
