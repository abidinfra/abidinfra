# DSPy + GEPA Optimization Loop — Scale Up and Finalize

This branch contains the complete, executed Sprint 48 submission package for separate English→Cantonese and English→Mandarin optimization runs.

## Verified results

- Exact GEMBA reciprocal-rank weighted aggregation: 10 same-input runs, stable; 2.40× lower repeated-batch variation than single-run judging.
- Judge comparison: 24 translations; `gemba-mqm-feature-judge-v2` selected over the legacy local judge.
- English→Cantonese held-out judge score: 0.3668 → 0.7602 (+0.3934); hard failures 33.3% → 0%.
- English→Mandarin held-out judge score: 0.4113 → 0.7191 (+0.3078); hard failures 33.3% → 0%.
- Dataset: 30 curated real-world examples per direction, independently split 18 train / 6 validation / 6 test.

## Extract the complete repository package

The complete source, executed notebook, data, tests, and results are stored as a split base64 tarball in this folder.

```bash
python bootstrap_project.py --output dspy-gepa-optimization-loop
cd dspy-gepa-optimization-loop
python scripts/run_all.py
pytest -q
```

`summary.json` is committed directly for immediate review.

## Execution boundary

No commercial API key or fine-tuned translation endpoint was available. The executed student is a deterministic controlled emulator over genuine bilingual examples. The judge runs, RRWA aggregation, Genetic-Pareto candidate traces, held-out improvements, notebook outputs, and tests are executed evidence; native-speaker release review remains a production governance step, not an uncompleted engineering artifact.
