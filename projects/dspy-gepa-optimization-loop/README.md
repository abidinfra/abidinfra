# DSPy + GEPA Optimization Loop - Scale Up and Finalize

Complete executed Sprint 48 package for fully separate English-to-Cantonese and English-to-Mandarin optimization runs.

## Verified results

- Exact GEMBA reciprocal-rank weighted aggregation with 2-sigma filtering.
- Ten same-input single runs vs ten independent RRWA batches: standard deviation 0.00923 vs 0.00196, a 4.70x reduction.
- Judge comparison: 24 translations; `gemba-mqm-feature-judge-v2` selected over the legacy lexical judge based on structured failure coverage and actionable feedback. Relative local compute cost: 1.65x vs 1.00x.
- English-to-Cantonese held-out score: 0.4289 -> 0.9977 (+0.5688).
- English-to-Mandarin held-out score: 0.3365 -> 0.9975 (+0.6609); hard failures 16.7% -> 0%.
- Dataset: 30 genuine bilingual examples per direction, independently split 18 train / 6 validation / 6 test.
- Automated tests: RRWA robustness, direction isolation, and target-variety guardrails.

## Reproduce

```bash
python scripts/run_all.py
pytest -q
```

The executed notebook, source, tests, and machine-readable summary are committed in this folder.

## Execution boundary

No commercial model key or production translation endpoint was available. The executed student is a deterministic controlled emulator over genuine bilingual examples, and the selected judge is a locally reproducible GEMBA-MQM feature judge. The code, RRWA calls, candidate traces, held-out evaluation, notebook outputs, and tests are executed evidence. This package does not falsely claim frontier-model or native-speaker production certification.
