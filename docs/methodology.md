# Methodology

## 1. Problem Definition

The Amazon ML Challenge 2026 task addressed **Business Entity Resolution**: determining whether records referring to businesses across different source systems represent the same underlying business entity.

The system operates at the entity-record level. For each S1 record, a set of candidate S2/S3 records is generated first, followed by pairwise matching and selection of the most likely candidate.

The objective is to build a reliable entity-matching system while controlling false positives, particularly in cases where multiple businesses have similar names, common address terms, or partially overlapping information.

---

## 2. Overall Pipeline

The implemented system follows a staged retrieval-and-ranking architecture:

```text
Source Records
      |
      v
Normalization
      |
      v
Candidate Generation / Blocking
      |
      v
Candidate Pairs
      |
      v
Feature Engineering
      |
      v
LightGBM Matching Model
      |
      v
Per-record Candidate Ranking
      |
      v
Thresholding / Match Selection
      |
      v
Final Entity Matches
```

The development process was iterative. The main experimental stages were referred to as V2, V3, and V4, with each stage modifying specific parts of the matching pipeline while keeping previously validated components fixed where possible.

---

## 3. Data Processing and Normalization

Source records were normalized before candidate generation and pairwise comparison.

Normalization was designed to reduce superficial differences between records while preserving information that could be useful for matching.

The processing pipeline maintained separate representations where appropriate, including normalized text and raw text. This allowed the system to use normalized representations for robust matching while retaining raw-text evidence for later comparison features.

Normalization and feature preparation were designed so that labels were not required to perform the basic text normalization process.

For learned statistics such as IDF-related information and dictionary-based processing, the experimental reports restricted learning to the appropriate training or unlabeled source data to reduce leakage risk.

---

## 4. Candidate Generation

Candidate generation, also referred to as **blocking** or **retrieval**, was used to reduce the number of possible pairwise comparisons.

Instead of comparing every S1 record against every possible S2/S3 record, blocking methods generated a smaller candidate set for each S1 entity.

The candidate-generation stage remained fixed for the main V2/V3 comparison. Later V4 work selectively re-retrieved and re-featurised France records after introducing France-specific normalization.

Candidate generation is an important constraint because the downstream model cannot select a true match that was not retrieved as a candidate.

A candidate-restricted oracle analysis established a diagnostic retrieval ceiling of:

**DEV Macro F0.5 = 0.99609**

This value represents the performance ceiling available under the candidate set when the correct candidate is assumed to be selected whenever it is present. It is **not a model score or achieved prediction score**.

The final matching system was therefore constrained by both:

1. Candidate-retrieval quality.
2. Downstream matching and ranking quality.

---

## 5. Feature Engineering

The matching system used multiple forms of pairwise evidence to distinguish genuine entity matches from non-matching candidates.

### 5.1 Name and Address Evidence

Features included comparisons between normalized business names and address components.

The V2 improvements introduced direct-evidence features including:

* IDF-weighted name-token agreement
* IDF-weighted address-token agreement
* Capped token rarity
* Rarest one-sided token information
* Premise-number comparisons
* Unit-number comparisons
* Raw-text agreement

These features were designed to give greater importance to informative matching evidence while reducing the influence of very common tokens.

### 5.2 Address and Structural Evidence

Address information was compared using multiple representations rather than relying on a single full-string similarity.

The feature set considered evidence such as:

* Premise numbers
* Unit numbers
* Address tokens
* Raw address text
* Token-level agreement
* Token rarity
* Structural inconsistencies

This was particularly useful for separating businesses that shared similar names but occupied different physical locations.

---

## 6. Direct Comparison Features

The V3 experiment extended the direct comparison approach with additional role-aware features.

The feature set included comparisons involving:

* Raw premise information
* Unit information
* Floor information
* House-number suffix conflicts
* Alphabetic address agreement
* Fuzzy unmatched name tokens
* Fuzzy unmatched address tokens
* Raw-text agreement

Address roles that could not be reliably identified were explicitly treated as **unknown** rather than being assigned an assumed role.

The V3 specialist model operated only on predictions inside the uncertain C3 probability interval:

```text
0.001 <= C3 probability <= 0.999
```

Outside this interval, the original C4 probability was retained.

The purpose of these direct comparison features was to provide additional evidence in difficult candidate pairs without introducing population-dependent information from unrelated source records.

---

## 7. LightGBM Matching

LightGBM was used as the primary pairwise matching model.

The model learned to distinguish matching and non-matching candidate pairs from the engineered pairwise features.

### 7.1 V2 Training

The V2 experiments increased the amount of training data used by the matching system from approximately 10% to 25% of the available TRAIN records.

The V2 improvements also incorporated direct-evidence features and a second-stage per-record refinement.

### 7.2 V3 Specialist Model

The V3 specialist model was trained using:

* 1,114,229 TRAIN records
* Direct comparison features
* Pairwise and C3 confidence features
* Grouped validation by country and normalized name
* Deterministic CPU configuration

The specialist model used:

* 127 leaves
* Minimum 250 records per leaf
* L2 regularization = 10
* 127 bins
* 4 threads
* A predeclared maximum of 2,200 iterations

The best iteration was **2,195**.

No production refit was performed after validation. The evaluated model was retained for the corresponding frozen experiment.

---

## 8. Per-record Ranking

The V2 pipeline introduced a second-stage per-record refinement.

For each source record, the strongest candidates were rescored using information from that record's own top candidate probabilities and probability margin.

The refinement operated only on information belonging to the current source record and did not use information from unrelated source records.

The purpose was to improve selection among closely competing candidates while avoiding population-dependent features that could change when unrelated records were duplicated or when the overall candidate distribution changed.

---

## 9. V3 Role-aware Refinement

V3 introduced a specialist LightGBM model over the direct comparison features described above.

The specialist operated on uncertain C3 predictions and retained the original C4 probability outside the specialist's operating range.

The final V3 threshold was frozen at:

**0.80**

The threshold was selected using the declared validation procedure rather than being changed after inspecting the reused CONF or stress results.

The V3 experiment also evaluated an alternative that removed retrieval-context information entirely. The best standalone and blended variants did not satisfy the predefined experimental gates and were rejected.

The V3 model did not use:

* Sibling agreement
* Cross-query counts
* External data
* Country-specific thresholds

The retrieval and candidate-selection stage remained unchanged for the main V3 experiment.

---

## 10. Evaluation Methodology

The primary evaluation metric used in the experiments was a per-S1 Macro F0.5 formulation:

```text
5TP / (5TP + 4FP + FN)
```

The metric was calculated per S1 record and then averaged across the evaluated S1 entities.

The use of F0.5 gives greater weight to precision than recall, which is relevant for entity resolution where accepting an incorrect business match can be particularly costly.

### 10.1 Validation Splits

The experiments used several evaluation partitions:

* **TRAIN:** used for model fitting and learning training-dependent statistics.
* **DEV:** used for model selection, threshold selection, and stress testing.
* **CONF:** a separate confirmation split that was opened once after the recipe and thresholds were frozen.
* **Test:** used for final candidate generation and prediction, but no independent labeled test score was available.

The reports explicitly note that CONF was reused for confirmation in later experiments and therefore should not be interpreted as a completely fresh independent holdout.

---

## 11. V2 Evaluation

The V2 C4 system produced the following local validation results:

| Evaluation | Baseline B0 |    Final C4 |
| ---------- | ----------: | ----------: |
| DEV        |     0.97785 | **0.98322** |
| CONF       |     0.97787 | **0.98321** |
| DEV stress |     0.97782 | **0.98324** |

The paired improvement on CONF was approximately:

**+0.00533**

with a reported 95% bootstrap confidence interval of approximately:

**[+0.00514, +0.00554]**

The V2 report attributed the improvement to several changes, including:

1. Removal of a population-dependent feature.
2. Addition of direct-evidence features.
3. Increasing the training population from approximately 10% to 25%.
4. Adding the per-record second-stage refinement.

The reported retrieval ceiling of **0.99609** remained above the achieved model performance and was treated only as a diagnostic ceiling.

---

## 12. V3 Evaluation

V3 was developed after the original C4 submission achieved a leaderboard Macro F0.5 of:

**0.970441**

The V3 model improved the local validation results:

| Evaluation                           | C4 Threshold 0.70 | V3 Threshold 0.80 |
| ------------------------------------ | ----------------: | ----------------: |
| DEV                                  |          0.983219 |      **0.984226** |
| Reused CONF                          |          0.983206 |      **0.984174** |
| DEV unmatched-FP weight ×4           |          0.979618 |      **0.982036** |
| Wrong-branch stress                  |          0.983242 |      **0.984302** |
| Wrong-branch stress, receiving twins |          0.977444 |      **0.978384** |
| DEV with no true matches             |          0.975234 |      **0.985132** |

The paired family-bootstrap interval for the reused-CONF improvement was reported as approximately:

**[+0.000861, +0.001079]**

This interval measures sampling variation within the evaluated dataset. It does not estimate the leaderboard gap and does not remove the limitation caused by reuse of CONF.

The V3 test export was completed using the frozen model and threshold. The resulting file contained:

* 1,732,544 S1 rows
* 1,631,363 S1 rows with matches
* 5,718,652 matched records
* Approximately 57.4% matched records

The official matching validator passed.

The V3 leaderboard score was **not measured in the reported experiment**, so the local V3 score must not be presented as a leaderboard score.

---

## 13. Stress Testing

Stress testing was used to evaluate robustness to difficult matching situations.

One stress suite was constructed from real labeled data by creating same-name groups with multiple addresses and removing one business from the available context.

The V2 stress analysis included:

* 31,050 same-name DEV groups with at least two addresses
* More than 100,000 real records involved in the constructed stress setting
* Retrieval of more than 120,000 related records

The stress experiments examined cases including:

* Wrong-address candidates
* Same-name businesses
* Zero-match records
* Duplicate or repeated query conditions
* Increased prevalence of distractor candidates

The experiments also checked whether learned features changed when unrelated source records were duplicated.

The reported results supported duplication invariance for the relevant feature designs and helped reject population-dependent feature constructions.

Stress testing was treated as a robustness diagnostic rather than as a substitute for an independent test set.

---

## 14. Cross-country Generalization Analysis

The V4 investigation focused on the gap between strong local validation and the lower observed leaderboard result.

The starting point was:

* C4 local DEV: **0.98322**
* C4 local CONF: **0.98321**
* C4 leaderboard: **0.970441**

Because labeled test data were unavailable, country-level proxy experiments were used to investigate possible generalization differences.

For example, models trained using one country and evaluated on another showed a measurable performance reduction compared with models that had access to training information from the evaluation country.

The reported proxy results included:

* US-only → India DEV: approximately **0.9295**
* India-only → US DEV: approximately **0.9455**

With corresponding in-country training information, performance was approximately:

* India: **0.9810**
* US: **0.9827**

These experiments were treated as evidence relevant to the hypothesis that an unseen country could introduce additional generalization difficulty. They did not directly measure the actual France test score.

---

## 15. France-specific Adaptation

The V4 experiment investigated France because the test data contained France records without corresponding labeled training data.

The analysis found that France had a larger uncertain prediction band than the observed US and India distributions.

Because test labels were unavailable, the actual France accuracy could not be directly measured.

### 15.1 France Locale Normalization

A France-specific normalization stage was introduced using unlabeled high-confidence information.

The normalization handled patterns including:

* Region and department naming differences
* Region-code representations
* `Hauts-de-France` versus `Nord`-style address representations
* `bis` / `ter` variants
* `b` / `t` abbreviations
* `CRS` / `cours` variants
* Roundabout-related address variants
* Apartment-related tokens
* Selected French legal-form terms in business names
* Variants such as `S.A.` formatting

France records were re-retrieved and re-featurised after this normalization.

US and India predictions in the C4-based V4 variants were kept unchanged so that any leaderboard difference could be isolated to the France-specific processing.

### 15.2 France Self-training

A France-specific pseudo-labeling experiment was also evaluated.

The model used:

* 6.19 million labeled US and India TRAIN rows
* Approximately 2.21 million France pseudo-labeled rows
* Approximately 20% of France records for the pseudo-labeled component

The France specialist was evaluated using confident C3 predictions as pseudo-labels.

The reported uncertainty-band analysis showed a reduction from approximately:

**7.2% → 4.3%**

after the France self-training approach.

This was treated as supporting evidence for the approach, not as a direct measurement of France test accuracy.

### 15.3 V4 Candidate Variants

Several candidate outputs were produced, including:

```text
output/matching_results.tsv
output/v4_c4fr_frp_t90/
output/v4_c4fr_t80/
output/v4_c4fr_frp_t80/
output/v4_v3fr_frp_t80/
```

The original C4 output remained associated with the measured leaderboard score of:

**0.970441**

The V4 variants had not yet received a confirmed leaderboard score in the reported experiment.

The V4 report contains an internal sequencing inconsistency: one candidate table labels the `v4_c4fr_frp_t90` variant as the recommended first upload, while the final action line instructs uploading `v4_c4fr_frp_t80` first. This documentation preserves that distinction rather than silently choosing between the two.

---

## 16. Data Leakage Controls

Several controls were used to reduce the risk of training/validation leakage.

The experimental reports specify that:

* Labels were not used during basic normalization.
* Training-dependent dictionaries were learned from TRAIN data.
* IDF statistics were derived from the appropriate unlabeled source catalog.
* V3 specialist training excluded the relevant DEV and CONF records.
* Specialist training used separate records for internal early stopping.
* The specialist did not use information from unrelated source records.
* No external data were introduced into the V3 specialist.
* Country-specific thresholds were not used in V3.
* No production refit was performed after validation.

These controls were intended to keep model selection and feature construction separate from later confirmation measurements.

---

## 17. Reproducibility and Correctness

The pipeline included several engineering safeguards to support reproducible execution.

These included:

* Configuration and manifest tracking
* Source and output fingerprints
* Atomic writes
* Checkpointing
* File-level recovery
* Memory monitoring
* Deterministic CPU configuration for the specialist model
* Validation of generated submission files
* Candidate-subset checks

A recovery test interrupted feature generation after several files and successfully resumed from the next checkpoint. The regenerated outputs were reported as byte-identical.

A reproduction test also regenerated the final V2 matching output and matched the previously recorded output hash.

The reported V2 matching output hash was:

```text
5a7f2c06...
```

The V3 test output hash was:

```text
fa607c39297b7d9000bf1145a1a2213a0863f99e55d15792c5328c7731ac487f
```

The official submission validator passed for the relevant generated outputs.

A complete from-scratch reproduction of the entire older retrieval and C3/C4 pipeline was **not** performed, so full end-to-end reproducibility from an empty environment was not claimed.

---

## 18. Computational Considerations

The experiments were designed to operate under constrained local hardware.

The reports describe sequential execution of heavy stages, bounded processing batches, checkpointing, and memory monitoring.

The V3 specialist training and prediction used four CPU threads and deterministic settings.

Observed specialist memory usage was reported in the approximate range of:

**0.25–1.1 GiB**

depending on the stage.

Heavy processing stages were executed sequentially to reduce resource contention.

---

## 19. Limitations

The following limitations are important when interpreting the results:

1. **No independently labeled test set was available.**
   France test performance therefore could not be directly measured.

2. **CONF was reused in later experiments.**
   It should not be interpreted as a completely fresh independent holdout for V3/V4.

3. **The outer split was entity-based but not fully family-disjoint across all processing stages.**

4. **V3 depended on frozen C3/C4 retrieval and model outputs.**

5. **The retrieval ceiling of 0.99609 is only a diagnostic candidate-set ceiling.**

6. **Local DEV improvements do not automatically translate into leaderboard improvements.**

7. **The V3 local score of approximately 0.9842 was not a leaderboard score.**

8. **The V4 France-specific modifications had not received confirmed leaderboard measurements in the reported experiment.**

9. **Cross-country proxy experiments do not directly establish the actual France test accuracy.**

10. **Stress-test weighting and distractor multipliers are diagnostic scenarios rather than exact replicas of the hidden test distribution.**

11. **A complete from-scratch reproduction of the older retrieval and C3/C4 pipeline was not performed.**

These limitations are retained to avoid overstating the experimental evidence.

---

## 20. Final Methodological Summary

The final development process followed a retrieval-and-ranking approach:

```text
Raw Business Records
        |
        v
Normalization
        |
        v
Candidate Generation / Blocking
        |
        v
Pairwise Feature Engineering
        |
        v
LightGBM Matching
        |
        v
Per-record Ranking
        |
        v
Role-aware Refinement
        |
        v
Thresholding
        |
        v
Submission Validation
```

The main methodological progression was:

**V2**

* Improved direct comparison evidence
* Increased training data
* Added per-record refinement
* Achieved approximately **0.9832 Macro F0.5** on DEV and CONF
* Produced the measured C4 leaderboard score of **0.970441**

**V3**

* Added role-aware direct comparison features
* Introduced a specialist LightGBM model for uncertain predictions
* Frozen threshold: **0.80**
* Improved local DEV performance to approximately **0.9842**
* Produced a validated test export
* No V3 leaderboard score was established in the reported experiment

**V4**

* Investigated the local-validation/leaderboard gap
* Examined cross-country generalization
* Introduced France-specific normalization
* Evaluated France pseudo-labeling/self-training
* Generated France-adapted candidate submissions
* Required leaderboard confirmation before claiming improvement

Overall, the project treated entity resolution as a combination of **candidate retrieval, pairwise evidence modeling, per-record ranking, and controlled adaptation to difficult data distributions**.

The methodology emphasizes measurable validation, explicit leakage controls, robustness testing, reproducibility safeguards, and transparent reporting of limitations rather than presenting diagnostic ceilings or local validation scores as leaderboard achievements.
