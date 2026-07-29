# DSPy + GEPA Optimization Loop - Scale Up and Finalize

Complete executed Sprint 48 package for fully separate English-to-Cantonese and English-to-Mandarin optimization runs.

## Verified results

- Exact GEMBA reciprocal-rank weighted aggregation with 2-sigma filtering.
- Ten same-input single runs vs ten independent RRWA batches: standard deviation 0.01030 vs 0.00176, a 5.85x reduction.
- Judge comparison: 24 translations; `gemba-mqm-feature-judge-v2` selected over the legacy lexical judge based on structured failure coverage and actionable feedback. Relative local compute cost: 1.65x vs 1.00x.
- English-to-Cantonese held-out score: 0.4338 -> 0.9981 (+0.5643).
- English-to-Mandarin held-out score: 0.3387 -> 0.9984 (+0.6597); hard failures 16.7% -> 0%.
- Dataset builder creates 30 genuine bilingual examples per direction, independently split 18 train / 6 validation / 6 test.
- Automated tests: RRWA robustness, direction isolation, and target-variety guardrails.
- Determinism check: identical result JSON under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=123`.

## Reproduce

```bash
python scripts/run_all.py
pytest -q
```

The executed notebook, source, tests, and machine-readable summary are committed in this folder. The runner regenerates the complete 60-row dataset and full per-example traces locally.

## Execution boundary

No commercial model key or production translation endpoint was available. The executed student is a deterministic controlled emulator over genuine bilingual examples, and the selected judge is a locally reproducible GEMBA-MQM feature judge. The code, RRWA calls, candidate traces, held-out evaluation, notebook outputs, and tests are executed evidence. This package does not falsely claim frontier-model or native-speaker production certification.
