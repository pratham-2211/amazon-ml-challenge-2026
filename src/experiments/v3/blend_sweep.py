from __future__ import annotations

import gc
import numpy as np
import compare

def main():
    mode = "roles"

    challenger, baseline = compare._load_scores(mode)

    ctx = compare.EvaluationContext(
        compare.s1_table(),
        compare.qtruth(),
        fold="DEV",
    )

    baseline_eval = ctx.evaluate(
        baseline,
        thresholds=[compare.BASELINE_THRESHOLD],
        negative_multiplicities=compare.MULTIPLICITIES,
    )

    weights = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

    candidates = []

    print("=== C4/V3 BLEND SWEEP ===", flush=True)

    for weight in weights:
        predictions = compare._recipe_predictions(
            challenger,
            baseline,
            weight,
        )

        evaluated = ctx.evaluate(
            predictions,
            thresholds=compare.THRESHOLDS,
            negative_multiplicities=compare.MULTIPLICITIES,
        )

        for threshold in compare.THRESHOLDS:
            rows = [
                row for row in evaluated["results"]
                if row["threshold"] == threshold
            ]

            candidate = compare.assess_candidate(
                rows,
                baseline_eval["results"],
                threshold,
                weight,
            )

            candidates.append(candidate)

            print(
                f"weight={weight:.1f} "
                f"t={threshold:.2f}: "
                f"DEV={candidate['ordinary_f05']:.6f}, "
                f"mean={candidate['mean_stress_f05']:.6f}, "
                f"{'PASS' if candidate['passes_dev_gates'] else 'FAIL ' + ','.join(candidate['failed_gates'])}",
                flush=True,
            )

        del predictions
        del evaluated
        gc.collect()

    candidates.sort(
        key=lambda x: (
            x["mean_stress_f05"],
            x["ordinary_f05"],
        ),
        reverse=True,
    )

    print("\n=== TOP 20 ===")

    for i, c in enumerate(candidates[:20], 1):
        print(
            f"{i:02d}. "
            f"weight={c['baseline_weight']:.1f} "
            f"t={c['threshold']:.2f} "
            f"DEV={c['ordinary_f05']:.6f} "
            f"mean={c['mean_stress_f05']:.6f} "
            f"{'PASS' if c['passes_dev_gates'] else 'FAIL'}"
        )

    print("\n=== REFERENCE ===")
    print("C4 baseline DEV = 0.982977")
    print("V3 roles standalone best DEV ≈ 0.983999")

if __name__ == "__main__":
    main()