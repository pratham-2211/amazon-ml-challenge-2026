# Results
This document summarizes the measured results, validation findings, diagnostic experiments, and documented submission outcomes of the Amazon ML Challenge 2026 Business Entity Resolution project.

## 1. Evaluation Overview

The project was evaluated using multiple stages of validation and diagnostic analysis rather than relying on a single metric.

The main evaluation stages were:

* **V2:** development validation, sealed CONF validation, and stress testing.
* **V3:** additional local validation of the role-aware refinement model and a frozen test export.
* **V4:** cross-country generalization analysis, self-training experiments, and France-specific adaptation.
* **Leaderboard:** the documented C4 submission achieved a Macro F0.5 score of **0.970441**.

The most important reported results are summarized below:

| Result                      | Score / Finding | Interpretation                            |
| --------------------------- | --------------: | ----------------------------------------- |
| V2 C4 DEV                   |     **0.98322** | Local development validation              |
| V2 C4 CONF                  |     **0.98321** | Sealed CONF validation                    |
| V3 DEV                      |    **0.984226** | Improved local validation                 |
| V3 CONF                     |    **0.984174** | Reused CONF validation                    |
| C4 Leaderboard              |    **0.970441** | Documented leaderboard result             |
| Candidate-restricted oracle |     **0.99609** | Diagnostic ceiling, not model performance |

The local validation results and leaderboard result are reported separately because they represent different evaluation settings. The candidate-restricted oracle is also kept separate because it represents the achievable ceiling when the correct candidate is already present in the retrieved candidate set.

## 2. V2 Results

### 2.1 Main Validation Results

The V2 pipeline evaluated the C4 configuration against the baseline using the project’s Macro F0.5 metric.

| Configuration |          DEV |         CONF |
| ------------- | -----------: | -----------: |
| Baseline B0   |      0.97785 |      0.97787 |
| C4            |  **0.98322** |  **0.98321** |
| Improvement   | **+0.00537** | **+0.00534** |

A paired family bootstrap analysis on the CONF comparison reported an improvement of approximately **+0.00533**, with a 95% confidence interval of **[+0.00514, +0.00554]**.

These results supported the V2 C4 configuration under the predefined evaluation procedure.

### 2.2 Stress-Test Results

The V2 system was also evaluated under several stress conditions.

| Stress condition                | Baseline |          C4 |
| ------------------------------- | -------: | ----------: |
| Overall stress DEV              |  0.97782 | **0.98324** |
| Stress twins receiving clusters |  0.97261 | **0.97744** |
| Stress zero-match twins         |   0.9662 |  **0.9724** |

The stress experiments were designed to examine robustness to difficult entity-resolution cases, including same-name groups, wrong-address clusters, and zero-match situations.

### 2.3 Candidate-Restricted Diagnostic Ceiling

A candidate-restricted oracle evaluation produced a Macro F0.5 score of **0.99609** on the DEV data.

This value is a **diagnostic ceiling**, not a model performance result. It measures the potential available within the retrieved candidate set when the correct candidate can be selected optimally.

Therefore, it should not be interpreted as the achieved accuracy or leaderboard performance of the C4 model.

## 3. V3 Results

### 3.1 Local Validation

V3 introduced a role-aware direct-feature refinement stage while keeping the underlying C3/C4 retrieval and candidate selection unchanged.

The frozen V3 configuration used a threshold of **0.80**.

| Evaluation |       C4 |           V3 |    Change |
| ---------- | -------: | -----------: | --------: |
| DEV        | 0.983219 | **0.984226** | +0.001007 |
| CONF       | 0.983206 | **0.984174** | +0.000968 |

On the reused CONF comparison, the paired family-bootstrap interval for the improvement was **[+0.000861, +0.001079]**.

The V3 results therefore showed a measurable improvement over C4 in the documented local validation experiments.

### 3.2 Additional Validation Findings

V3 also showed improvements under several diagnostic conditions:

| Evaluation                 |       C4 |           V3 |
| -------------------------- | -------: | -----------: |
| DEV unmatched-FP weight ×4 | 0.979618 | **0.982036** |
| Wrong-branch stress        | 0.983242 | **0.984302** |
| Stress receiving twins     | 0.977444 | **0.978384** |
| DEV no-true-match cases    | 0.975234 | **0.985132** |

These results were used to examine the behavior of the refinement stage under difficult matching conditions.

### 3.3 V3 Test Export

A frozen V3 model was also used to generate a test submission.

Documented export statistics were:

* **1,732,544** S1 rows
* **1,631,363** S1 rows with matches
* **5,718,652** matched records
* **57.4%** of records matched
* Decision threshold: **0.80**
* Baseline blend weight: **0**
* Official submission validator: **PASS**

The V3 test export did not have a documented leaderboard score in the experiment report. Therefore, the V3 local validation score should not be presented as a leaderboard result.

## 4. V4 Results

### 4.1 Cross-Country Generalization

V4 investigated whether the local validation-to-leaderboard gap could be related to country-specific generalization.

Proxy experiments trained on one country and evaluated on another showed a substantial reduction compared with in-country validation:

| Training → Evaluation | Baseline | Self-training |
| --------------------- | -------: | ------------: |
| US → India            |  0.92951 |   **0.93441** |
| India → US            |  0.94549 |   **0.94525** |

These experiments suggested that performance could degrade when the target country was not represented in the training data.

The experiments were used as a **generalization proxy**. They do not provide a direct measurement of France leaderboard accuracy.

### 4.2 Self-Training

Self-training was investigated as a possible method for adapting the model to an unseen country.

For the US → India direction, one round of pseudo-labeling improved the reported result across the tested thresholds. For the India → US direction, the effect was approximately neutral, with a small decrease at the best baseline comparison.

A two-round self-training experiment was also tested and was rejected because it did not provide sufficient additional improvement.

The results therefore provided evidence that self-training could help in some cross-country transfer settings, but its effect was not uniformly positive across directions.

### 4.3 France-Specific Adaptation

France received separate treatment because the test set contained no corresponding France training data and showed a larger uncertain-score region than the observed US and India development data.

Two main adaptations were evaluated:

1. **French-locale normalization**

   * Normalized French regional and departmental naming variations.
   * Handled selected French address abbreviations and variants.
   * Normalized selected legal-form and apartment/address tokens.
   * France candidates were re-retrieved and re-featurised using the adapted normalization.

2. **France self-training**

   * Used high-confidence pseudo-labels from the available US and India data.
   * Added pseudo-labeled France records for adaptation.
   * Reduced the France uncertain-score band from approximately **7.2% to 4.3%**.

These measurements are diagnostic changes in the model's score distribution and do **not** represent measured France accuracy.

### 4.4 V4 Submission Variants

The documented V4 candidate outputs included:

* C4 baseline output with leaderboard score **0.970441**
* France locale-normalized C4 variants
* France locale + self-training variants
* V3-based France variants

For the C4-based V4 variants, the US and India predictions were kept byte-identical to the original C4 output. This was intended to isolate the effect of the France-specific changes.

The V4 experiment report did not document a confirmed leaderboard score for these modified variants. Therefore, no V4 leaderboard improvement is claimed here.

## 5. Leaderboard Result

The documented C4 submission achieved a **Macro F0.5 score of 0.970441** on the Amazon ML Challenge 2026 leaderboard.

This is the primary externally measured competition result documented in the project.

The leaderboard score should be distinguished from the higher local validation scores obtained during development:

* **0.970441** — documented C4 leaderboard result
* **0.984226** — V3 DEV local validation
* **0.984174** — V3 reused CONF validation
* **0.99609** — candidate-restricted diagnostic ceiling

The difference between local validation and leaderboard performance motivated the V4 generalization and France-specific investigations.

No claim is made that the V3 or V4 configurations achieved a particular leaderboard score because the experiment documentation does not contain a confirmed leaderboard measurement for those variants.

## 6. Measured vs Unmeasured Results

To keep the project results reproducible and technically accurate, measured results are separated from diagnostic findings and unverified estimates.

### Measured Results

The following results were directly obtained from the documented experiments:

* V2 C4 DEV: **0.98322**
* V2 C4 CONF: **0.98321**
* V3 DEV: **0.984226**
* V3 reused CONF: **0.984174**
* C4 leaderboard: **0.970441**
* Candidate-restricted diagnostic ceiling: **0.99609**
* V3 test export validation: **PASS**
* V4 cross-country proxy results
* V4 France uncertainty-band reduction: **7.2% → 4.3%**

### Unmeasured or Unconfirmed Results

The following should not be presented as confirmed competition results:

* V3 leaderboard performance
* V4 leaderboard performance
* Actual France-only test accuracy
* Any inferred overall leaderboard score for a V4 France variant

The experiment reports explicitly distinguish these measurements from hypotheses or diagnostic analyses.

In particular, estimates based on hypothetical France performance are not included as achieved results.

## 7. Limitations

The reported results should be interpreted within the scope of the available evaluation setup.

* The documented **0.970441 leaderboard score** corresponds to the C4 submission and should not be attributed to later V3 or V4 variants.
* The V3 CONF evaluation reused the CONF set from the V2 experiment and was therefore not a newly sealed independent holdout.
* The V3 evaluation used the existing C3/C4 retrieval and candidate-generation pipeline as a frozen dependency.
* The outer validation split was entity-based but was not fully family-disjoint across every stage of the complete pipeline.
* France-specific accuracy was not directly measured with an authorized labeled France evaluation set.
* Cross-country experiments were proxy experiments for studying generalization and should not be interpreted as direct leaderboard predictions.
* Stress-test and unmatched-negative weighting experiments are diagnostic analyses rather than independent competition benchmarks.
* A complete from-scratch rerun of the older retrieval, C3, and C4 stages was not performed.
* The project therefore reports only the results that were directly measured and documented, without converting diagnostic findings into unsupported performance claims.

## 8. Final Results Summary

The experiments demonstrate a progression from the baseline C4 entity-resolution pipeline toward increasingly specialized validation and adaptation strategies.

The main documented findings are:

1. **V2 C4** improved the local validation score from approximately **0.9779 to 0.9832**, supported by direct-evidence features, increased training data, and per-record refinement.
2. **V3** produced a further local improvement, reaching **0.984226 on DEV** and **0.984174 on the reused CONF set**.
3. **V3 stress and difficult-case evaluations** showed additional improvements in several diagnostic settings, including wrong-branch and no-true-match cases.
4. The documented **C4 leaderboard result was 0.970441**.
5. The gap between local validation and leaderboard performance motivated **V4 cross-country generalization experiments**.
6. V4 experiments showed that cross-country transfer could reduce performance in the tested proxy settings and that self-training could provide improvements in some transfer directions.
7. **France-specific normalization and self-training** changed the model's score distribution, including a reduction in the France uncertain-score band, but France accuracy was not directly measured.
8. The **0.99609 candidate-restricted oracle** demonstrates remaining potential within the retrieved candidate set, but it is a diagnostic ceiling rather than achieved model performance.

Overall, the project documents a reproducible experimental progression from candidate generation and supervised matching toward direct-evidence refinement, role-aware modeling, stress testing, and country-specific adaptation.

All reported performance values are presented according to their actual evaluation setting, and unmeasured leaderboard or France-specific results are intentionally not claimed.
