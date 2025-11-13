# Hybrid DeepSeek Orchestrator (Phase 1 Update)

**Date:** November 12, 2025  
**Component:** `core/universal_ai_analyzer.py`

## Summary
- Local NLP (spaCy + rules via `LocalAIAnalyzer`) now *always* runs first.
- DeepSeek runs on every request (when API key available): if the local pass is incomplete we treat it as a gap-fill, otherwise we use the DeepSeek response for cross-checking + enrichment before merging.
- Analyzer outputs include `attribute_provenance` + `analysis_metadata` so downstream stages can see which sections came from local tools vs DeepSeek enrichment.

## Telemetry Snapshot
Each `CanonicalProblemSpec` now carries:

| Field | Description |
| --- | --- |
| `attribute_provenance` | Map of high-level sections (`domain`, `objects`, `constraints`, …) to source tags (`local`, `deepseek`, `local+deepseek`). |
| `analysis_metadata.local` | Object/relationship counts, confidence, runtime, and any local analyzer error. |
| `analysis_metadata.deepseek` | Whether DeepSeek ran, confidence stats, and API errors (if any). |
| `analysis_metadata.merge` | Reason for invoking DeepSeek plus the final provenance map. |

Use `UniversalAIAnalyzer.last_analysis_telemetry` for the most recent run, or inspect `spec.analysis_metadata` after `analyze()`.

## Merge Rules (simplified)
1. Start with the local spec (`copy.deepcopy`) when available.
2. Bring over DeepSeek data only when the local section is empty or can be meaningfully enriched.
3. Domain/problem type upgrade happens only if the local run reported `UNKNOWN` or blank.
4. Lists (`objects`, `relationships`, `constraints`, `applicable_laws`) are merged by ID/name with duplicate-safe enrichment.
5. Dict sections (`environment`, `physics_context`, `geometry`) receive key-by-key updates; provenance flips to `local+deepseek` when both contributed.

## How to Consume the Telemetry
```python
spec = analyzer.analyze(problem_text)
print(spec.attribute_provenance)
# {'domain': 'local', 'objects': 'local+deepseek', 'constraints': 'deepseek', ...}

telemetry = spec.analysis_metadata
print(telemetry['local'])
# {'available': True, 'objects': 2, 'relationships': 1, 'confidence': 0.52, ...}
```

This makes it easy to audit how much of a scene originated from local parsing vs DeepSeek reasoning, aligning with the roadmap’s “hybrid orchestrator” milestone.
