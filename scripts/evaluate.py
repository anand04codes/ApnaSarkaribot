"""
Evaluation script for SarkariSach detection pipeline.
Evaluates realistic scam and genuine samples, calculating:
- Accuracy, Precision, Recall, F1-Score
- 2x2 Confusion Matrix
- Category-level breakdown
"""
import sys
import json
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.rules_engine import IndianScamRulesEngine
from app.core.fusion import FusionEngine


def load_samples(samples_dir: Path):
    samples = []
    for f in sorted(samples_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            samples.append(json.load(fp))
    return samples


def run_evaluation():
    engine = IndianScamRulesEngine(data_dir=backend_path / "app" / "data")
    
    samples_base = backend_path / "tests" / "samples"
    scam_samples = load_samples(samples_base / "scams")
    genuine_samples = load_samples(samples_base / "genuine")

    tp = 0  # Scam detected as LIKELY SCAM or SUSPICIOUS
    fn = 0  # Scam falsely labeled as LOOKS GENUINE
    tn = 0  # Genuine correctly labeled as LOOKS GENUINE
    fp = 0  # Genuine falsely labeled as LIKELY SCAM or SUSPICIOUS

    results = []

    print("\n" + "="*80)
    print(" SARKARISACH DETECTION PIPELINE EVALUATION BENCHMARK")
    print("="*80)

    # 1. Evaluate Scams
    print("\n--- EVALUATING SCAM DATASET (16 Realistic Indian Scams) ---")
    for s in scam_samples:
        rules_eval = engine.evaluate(s["text"])
        fused = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=None, language="en")
        
        is_scam_flagged = (fused.verdict in ["LIKELY SCAM", "SUSPICIOUS"])
        if is_scam_flagged:
            tp += 1
            status = "PASS [DETECTED]"
        else:
            fn += 1
            status = "FAIL [MISSED]"

        results.append({
            "id": s["id"],
            "title": s["title"],
            "category": s["category"],
            "ground_truth": s["expected_verdict"],
            "predicted": fused.verdict,
            "risk_score": fused.risk_score,
            "matched_rules": len(rules_eval.matched_rules),
            "status": status
        })
        print(f"[{status}] {s['id']} | Score: {fused.risk_score:3d} | Verdict: {fused.verdict:12s} | {s['title']}")

    # 2. Evaluate Genuine
    print("\n--- EVALUATING GENUINE DATASET (9 Realistic Indian Official Alerts) ---")
    for g in genuine_samples:
        rules_eval = engine.evaluate(g["text"])
        fused = FusionEngine.fuse(rules_eval=rules_eval, llm_eval=None, language="en")
        
        is_genuine = (fused.verdict == "LOOKS GENUINE")
        if is_genuine:
            tn += 1
            status = "PASS [GENUINE]"
        else:
            fp += 1
            status = "FAIL [FALSE ALARM]"

        results.append({
            "id": g["id"],
            "title": g["title"],
            "category": g["category"],
            "ground_truth": g["expected_verdict"],
            "predicted": fused.verdict,
            "risk_score": fused.risk_score,
            "matched_rules": len(rules_eval.matched_rules),
            "status": status
        })
        print(f"[{status}] {g['id']} | Score: {fused.risk_score:3d} | Verdict: {fused.verdict:12s} | {g['title']}")

    # Calculate Metrics
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "="*80)
    print(" CONFUSION MATRIX & PERFORMANCE METRICS")
    print("="*80)
    print(f" Total Samples Tested   : {total}")
    print(f" True Positives  (TP)   : {tp:2d} (Scams correctly flagged)")
    print(f" True Negatives  (TN)   : {tn:2d} (Genuine correctly verified)")
    print(f" False Positives (FP)   : {fp:2d} (False alarms on genuine)")
    print(f" False Negatives (FN)   : {fn:2d} (Missed scams)")
    print("-" * 40)
    print(" CONFUSION MATRIX:")
    print("                  Predicted Scam    Predicted Genuine")
    print(f" Actual Scam           {tp:2d}                {fn:2d}")
    print(f" Actual Genuine        {fp:2d}                {tn:2d}")
    print("-" * 40)
    print(f" ACCURACY   : {accuracy * 100:.2f}%")
    print(f" PRECISION  : {precision * 100:.2f}%")
    print(f" RECALL     : {recall * 100:.2f}%")
    print(f" F1-SCORE   : {f1 * 100:.2f}%")
    print("="*80 + "\n")

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "total": total,
        "results": results
    }

if __name__ == "__main__":
    run_evaluation()

