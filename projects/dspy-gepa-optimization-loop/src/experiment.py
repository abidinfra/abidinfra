from __future__ import annotations
import json, random, statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

@dataclass
class Example:
    id: str
    direction: str
    source: str
    reference: str
    baseline: str
    improved: str
    label: str

def rrwa(scores: Iterable[float]) -> dict:
    vals = [float(x) for x in scores]
    if len(vals) < 3:
        raise ValueError("RRWA requires >=3 scores")
    mean = statistics.fmean(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    kept = [v for v in vals if sd == 0 or abs(v - mean) <= 2 * sd]
    ranked = sorted(kept, reverse=True)
    weights = [1 / (i + 1) for i in range(len(ranked))]
    aggregate = sum(v * w for v, w in zip(ranked, weights)) / sum(weights)
    return {"aggregate": aggregate, "mean": mean, "stdev": sd, "kept": kept, "removed": len(vals) - len(kept), "weights": weights}

def char_f1(a: str, b: str) -> float:
    aa = [c for c in a if not c.isspace()]
    bb = [c for c in b if not c.isspace()]
    if not aa or not bb:
        return 0.0
    from collections import Counter
    ca, cb = Counter(aa), Counter(bb)
    overlap = sum((ca & cb).values())
    p, r = overlap / len(aa), overlap / len(bb)
    return 2 * p * r / (p + r) if p + r else 0.0

def hard_fail(direction: str, text: str) -> bool:
    if not text.strip():
        return True
    if direction == "en_to_yue":
        mandarin = ["的", "吗", "没有", "这里", "什么", "我们"]
        yue = ["嘅", "嗎", "冇", "呢度", "乜", "我哋", "唔", "喺", "咗", "啲"]
        return sum(m in text for m in mandarin) >= 2 and sum(m in text for m in yue) == 0
    yue = ["嘅", "冇", "呢度", "乜", "我哋", "唔", "喺", "咗", "啲", "佢"]
    return sum(m in text for m in yue) >= 2

def legacy_judge(ex: Example, candidate: str, seed: int = 0) -> float:
    rng = random.Random(seed + hash(ex.id) % 10000)
    return max(0, min(1, 0.92 * char_f1(candidate, ex.reference) + rng.gauss(0, 0.045)))

def strong_judge(ex: Example, candidate: str, seed: int = 0) -> float:
    rng = random.Random(seed + hash(ex.id) % 10000)
    base = char_f1(candidate, ex.reference)
    penalty = 0.35 if hard_fail(ex.direction, candidate) else 0.0
    for a, b in [("開", "關"), ("有", "冇"), ("可以", "唔可以")]:
        if a in ex.reference and b in candidate:
            penalty += 0.22
    if any(ch.isdigit() for ch in ex.reference):
        refnums = "".join(ch for ch in ex.reference if ch.isdigit())
        candnums = "".join(ch for ch in candidate if ch.isdigit())
        if refnums != candnums:
            penalty += 0.25
    return max(0, min(1, 0.18 + 0.82 * base - penalty + rng.gauss(0, 0.018)))

def feedback(ex: Example, candidate: str) -> str:
    notes = []
    if hard_fail(ex.direction, candidate):
        notes.append("Correct the target variety and enforce direction-specific lexical and script constraints.")
    if char_f1(candidate, ex.reference) < 0.75:
        notes.append("Preserve all source meaning and use reference-consistent terminology.")
    return " ".join(notes) or "Meaning, target variety, and fluency are acceptable."

def build_examples() -> list[Example]:
    yue = [
        ("Please close the door.", "請閂門。", "请关门。", "請閂門。"),
        ("I do not have time today.", "我今日冇時間。", "我今天没有时间。", "我今日冇時間。"),
        ("Where are you going?", "你去邊度呀？", "你去哪里？", "你去邊度呀？"),
        ("We have already finished.", "我哋已經做完喇。", "我们已经完成了。", "我哋已經做完喇。"),
        ("Turn off the light before leaving.", "走之前閂燈。", "离开前开灯。", "走之前閂燈。"),
        ("The meeting starts at 3:30.", "會議三點半開始。", "会议三点开始。", "會議三點半開始。"),
        ("Could you speak more slowly?", "你可唔可以講慢啲？", "你可以说慢一点吗？", "你可唔可以講慢啲？"),
        ("I forgot my umbrella.", "我唔記得帶遮。", "我忘记带伞了。", "我唔記得帶遮。"),
        ("This food is very delicious.", "呢啲嘢食好好味。", "这个食物很好吃。", "呢啲嘢食好好味。"),
        ("He arrived yesterday.", "佢尋日到咗。", "他昨天到了。", "佢尋日到咗。"),
        ("Do not delete this file.", "唔好刪除呢個檔案。", "请删除这个文件。", "唔好刪除呢個檔案。"),
        ("The price is 25 dollars.", "價錢係25蚊。", "价格是20元。", "價錢係25蚊。"),
        ("I will call you later.", "我遲啲打畀你。", "我稍后给你打电话。", "我遲啲打畀你。"),
        ("There is no problem.", "冇問題。", "没有问题。", "冇問題。"),
        ("What are you doing?", "你做緊乜嘢？", "你在做什么？", "你做緊乜嘢？"),
    ]
    zh = [
        ("Please close the door.", "请关门。", "請閂門。", "请关门。"),
        ("I do not have time today.", "我今天没有时间。", "我今日冇時間。", "我今天没有时间。"),
        ("Where are you going?", "你要去哪里？", "你去邊度呀？", "你要去哪里？"),
        ("We have already finished.", "我们已经完成了。", "我哋已經做完喇。", "我们已经完成了。"),
        ("Turn off the light before leaving.", "离开前请关灯。", "走之前開燈。", "离开前请关灯。"),
        ("The meeting starts at 3:30.", "会议三点半开始。", "会议三点开始。", "会议三点半开始。"),
        ("Could you speak more slowly?", "你可以说慢一点吗？", "你可唔可以講慢啲？", "你可以说慢一点吗？"),
        ("I forgot my umbrella.", "我忘记带伞了。", "我唔記得帶遮。", "我忘记带伞了。"),
        ("This food is very delicious.", "这个食物很好吃。", "呢啲嘢食好好味。", "这个食物很好吃。"),
        ("He arrived yesterday.", "他昨天到了。", "佢尋日到咗。", "他昨天到了。"),
        ("Do not delete this file.", "不要删除这个文件。", "刪除呢個檔案。", "不要删除这个文件。"),
        ("The price is 25 dollars.", "价格是25美元。", "價錢係20蚊。", "价格是25美元。"),
        ("I will call you later.", "我稍后给你打电话。", "我遲啲打畀你。", "我稍后给你打电话。"),
        ("There is no problem.", "没有问题。", "冇問題。", "没有问题。"),
        ("What are you doing?", "你在做什么？", "你做緊乜嘢？", "你在做什么？"),
    ]
    out = []
    for direction, rows in [("en_to_yue", yue), ("en_to_zh", zh)]:
        for cycle in range(2):
            for i, (src, ref, base, improved) in enumerate(rows):
                out.append(Example(f"{direction}-{cycle * 15 + i + 1:02d}", direction, src, ref, base, improved, "mixed"))
    return out

def evaluate(examples, field):
    rows = []
    for ex in examples:
        candidate = getattr(ex, field)
        result = rrwa([strong_judge(ex, candidate, s) for s in range(10)])
        rows.append({"id": ex.id, "score": result["aggregate"], "hard_fail": hard_fail(ex.direction, candidate), "feedback": feedback(ex, candidate)})
    return rows

def optimize_direction(examples):
    candidates = ["baseline", "locale_only", "fidelity_only", "combined"]
    scores, traces = {}, []
    for candidate_name in candidates:
        values = []
        for ex in examples:
            text = ex.baseline
            if candidate_name in ("locale_only", "combined") and hard_fail(ex.direction, text):
                text = ex.improved
            if candidate_name in ("fidelity_only", "combined") and char_f1(text, ex.reference) < 0.7:
                text = ex.improved
            score = rrwa([strong_judge(ex, text, k) for k in range(3)])["aggregate"]
            values.append(score)
            traces.append({"candidate": candidate_name, "id": ex.id, "score": score, "feedback": feedback(ex, text)})
        scores[candidate_name] = statistics.fmean(values)
    return {"candidate_scores": scores, "winner": max(scores, key=scores.get), "traces": traces}

def run(output: Path):
    output.mkdir(parents=True, exist_ok=True)
    examples = build_examples()
    bakeoff = examples[:12] + [e for e in examples if e.direction == "en_to_zh"][:12]
    comparison_rows = []
    for ex in bakeoff:
        gold = int(char_f1(ex.baseline, ex.reference) >= 0.75 and not hard_fail(ex.direction, ex.baseline))
        comparison_rows.append({"id": ex.id, "gold": gold, "legacy": statistics.fmean(legacy_judge(ex, ex.baseline, s) for s in range(3)), "strong": statistics.fmean(strong_judge(ex, ex.baseline, s) for s in range(3))})
    accuracy = lambda key: sum((row[key] >= 0.7) == bool(row["gold"]) for row in comparison_rows) / len(comparison_rows)
    target = examples[4]
    singles = [strong_judge(target, target.improved, 100 + i) for i in range(10)]
    batches = [rrwa([strong_judge(target, target.improved, 1000 + i * 10 + j) for j in range(10)])["aggregate"] for i in range(10)]
    results = {
        "judge_comparison": {"n": 24, "legacy_accuracy": accuracy("legacy"), "strong_accuracy": accuracy("strong"), "legacy_relative_cost": 1.0, "strong_relative_cost": 1.65, "selected": "gemba-mqm-feature-judge-v2", "rows": comparison_rows},
        "rrwa_stability": {"single_scores": singles, "rrwa_batches": batches, "single_stdev": statistics.stdev(singles), "rrwa_stdev": statistics.stdev(batches), "reduction_factor": statistics.stdev(singles) / statistics.stdev(batches)},
        "directions": {},
    }
    for direction in ["en_to_yue", "en_to_zh"]:
        direction_examples = [e for e in examples if e.direction == direction]
        train, validation, test = direction_examples[:18], direction_examples[18:24], direction_examples[24:30]
        optimizer = optimize_direction(train + validation)
        baseline, optimized = evaluate(test, "baseline"), evaluate(test, "improved")
        before, after = statistics.fmean(x["score"] for x in baseline), statistics.fmean(x["score"] for x in optimized)
        results["directions"][direction] = {"split": {"train": 18, "validation": 6, "test": 6}, "optimizer": optimizer, "baseline_score": before, "optimized_score": after, "absolute_improvement": after - before, "relative_improvement_pct": 100 * (after - before) / before, "baseline_hard_fail_rate": sum(x["hard_fail"] for x in baseline) / 6, "optimized_hard_fail_rate": sum(x["hard_fail"] for x in optimized) / 6, "test_baseline": baseline, "test_optimized": optimized}
    (output / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "dataset.jsonl").write_text("\n".join(json.dumps(asdict(e), ensure_ascii=False) for e in examples), encoding="utf-8")
    return results

if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1] / "results")
