\# Experiments



This document records the major experimental stages of the Amazon ML Challenge 2026 Business Entity Resolution project.



The experiments progressed from the V2 C4 pipeline to the V3 role-aware refinement and finally to the V4 France-specific adaptation.



All reported metrics are identified by evaluation split and experiment stage. Diagnostic ceilings, local validation scores, and leaderboard scores are kept separate.



\---



\## 1. Experiment Overview



The project followed three major experimental stages:



| Version | Main Objective                        | Major Change                                                 | Key Result                          |

| ------- | ------------------------------------- | ------------------------------------------------------------ | ----------------------------------- |

| V2 / C4 | Improve the baseline matcher          | Direct evidence + more training data + per-record refinement | DEV ≈ 0.9832                        |

| V3      | Improve difficult candidate decisions | Role-aware direct features + specialist LightGBM             | DEV ≈ 0.9842                        |

| V4      | Investigate leaderboard gap           | France-specific normalization + pseudo-labeling              | Leaderboard result not yet measured |



The original C4 submission achieved a measured leaderboard Macro F0.5 of:



\*\*0.970441\*\*



This value is kept separate from the higher local DEV/CONF validation results.



\---



\# 2. V2 Experiments



\## 2.1 Objective



The V2 experiments focused on improving the baseline entity-resolution pipeline while maintaining the existing candidate-generation framework.



The main areas investigated were:



1\. Population-dependent features

2\. Direct pairwise evidence

3\. Training-data scale

4\. Per-record candidate refinement

5\. Robustness to difficult matching conditions



\---



\## 2.2 Population Feature Removal



One population-dependent feature, `s1\_rank1\_deg`, was investigated because its behavior changed under difficult matching conditions.



The feature was removed from the final V2 configuration.



The DEV performance was approximately neutral at:



\*\*0.97791\*\*



However, under a zero-match stress condition with a threshold of 0.7, the feature showed an undesirable trade-off, with performance changing from approximately:



\*\*0.980 → 0.962\*\*



The feature was therefore not retained in the final pipeline.



\### Finding



Population-dependent information was treated cautiously because it could introduce sensitivity to the surrounding candidate population.



\---



\## 2.3 Direct-Evidence Features



The next experiment introduced direct pairwise evidence features.



These included:



\* IDF-weighted name-token agreement

\* IDF-weighted address-token agreement

\* Capped token rarity

\* Rarest one-sided token

\* Premise-number equality

\* Unit-number equality

\* Number containment

\* Number closeness

\* Raw-text agreement



The addition of these features produced an improvement of approximately:



\*\*+0.0027 Macro F0.5\*\*



relative to the corresponding baseline configuration.



\### Finding



Direct evidence between the two records provided useful information beyond the existing feature set.



\---



\## 2.4 Increasing Training Data



The training population was increased from approximately 10% of the available training records to approximately 25%.



This corresponded to approximately:



\*\*15.5 million candidate pairs\*\*



in the larger training configuration.



The reported improvement was approximately:



\*\*+0.0015 Macro F0.5\*\*



\### Finding



Increasing the amount of training data improved the matcher while remaining within the available computational constraints.



\---



\## 2.5 Per-record Second-stage Refinement



A second-stage refinement was introduced for each S1 record.



The refinement used:



\* The record's top candidate probabilities

\* The probability margin between candidates

\* The current record's own candidate set



The refinement did not use information from unrelated source records.



The reported improvement was approximately:



\*\*+0.0012 Macro F0.5\*\*



\### Finding



Per-record ranking information helped distinguish closely competing candidates without introducing cross-query population features.



\---



\## 2.6 V2 C4 Evaluation



The resulting C4 pipeline produced the following results:



| Evaluation | Baseline B0 |          C4 |

| ---------- | ----------: | ----------: |

| DEV        |     0.97785 | \*\*0.98322\*\* |

| CONF       |     0.97787 | \*\*0.98321\*\* |

| DEV stress |     0.97782 | \*\*0.98324\*\* |



The paired CONF improvement was approximately:



\*\*+0.00533\*\*



with a reported 95% bootstrap confidence interval of approximately:



\*\*\[+0.00514, +0.00554]\*\*



\---



\## 2.7 V2 Stress Experiments



The V2 pipeline was evaluated under additional difficult conditions.



Reported results included:



| Stress Condition               | Baseline |          C4 |

| ------------------------------ | -------: | ----------: |

| Overall stress                 |  0.97782 | \*\*0.98324\*\* |

| Same-name/wrong-address stress |  0.97261 | \*\*0.97744\*\* |

| Zero-match twins               |   0.9662 |  \*\*0.9724\*\* |



The experiments also tested distractor prevalence and candidate duplication behavior.



The final feature design was checked for invariance when unrelated source records were duplicated.



\---



\## 2.8 Candidate-restricted Oracle



A candidate-restricted oracle experiment produced:



\*\*0.99609 Macro F0.5\*\*



on DEV.



This result represents a diagnostic ceiling under the existing candidate set.



It assumes that when the correct candidate is present, the correct candidate can be selected.



Therefore:



> \*\*0.99609 is not the model's achieved score and must not be reported as the final model performance.\*\*



The result instead indicates that candidate retrieval was not the only source of error; ranking and matching decisions also contributed to the remaining gap.



\---



\# 3. V2 Rejected / Investigated Approaches



Several approaches were investigated and either removed or not used in the final showcase pipeline.



\### 3.1 Population-dependent Ranking Feature



`S1\_rank1\_deg` was removed because its behavior under zero-match stress was unfavorable.



\### 3.2 E10 Sibling-feature Experiment



An alternative sibling-feature experiment was evaluated and produced approximately:



\*\*0.933 Macro F0.5\*\*



This was substantially below the stronger C4 configuration and was not retained.



\### 3.3 All-candidate C4 Diagnostic



An all-candidate C4 configuration was evaluated during development.



Its score is intentionally \*\*not included in the public project results\*\* because it was a diagnostic experiment and does not represent the final candidate-generation pipeline.



\---



\# 4. V3 Experiments



\## 4.1 Objective



V3 was developed after the C4 submission produced a leaderboard score of:



\*\*0.970441\*\*



while local validation remained approximately:



\*\*0.9832\*\*



The goal was to improve difficult candidate decisions without changing the core retrieval system.



\---



\## 4.2 Role-aware Direct Features



V3 introduced additional direct comparison features.



These included:



\* Raw premise roles

\* Unit roles

\* Floor roles

\* House-number suffix conflicts

\* Alphabetic address agreement

\* Fuzzy unmatched name tokens

\* Fuzzy unmatched address tokens

\* Raw-text agreement



Unknown address roles were represented as unknown rather than being assigned an assumed role.



\---



\## 4.3 Specialist LightGBM



A specialist LightGBM model was introduced for uncertain C3 predictions.



The specialist was applied only when:



```text

0.001 <= C3 probability <= 0.999

```



Outside this interval, the original C4 probability was retained.



The specialist model used:



\* 1,114,229 TRAIN records

\* 127 leaves

\* Minimum 250 records per leaf

\* L2 regularization = 10

\* 127 bins

\* 4 CPU threads

\* Maximum 2,200 iterations

\* Best iteration = 2,195



The model did not use:



\* Sibling agreement

\* Cross-query counts

\* External data

\* Country-specific thresholds



\---



\## 4.4 Threshold Selection



Several thresholds between 0.70 and 0.85 were evaluated.



The final threshold was frozen at:



\*\*0.80\*\*



The threshold was selected according to the declared experimental procedure rather than being changed after observing later confirmation results.



\---



\## 4.5 V3 Evaluation



The main V3 results were:



| Evaluation                 |       C4 |           V3 |

| -------------------------- | -------: | -----------: |

| DEV                        | 0.983219 | \*\*0.984226\*\* |

| Reused CONF                | 0.983206 | \*\*0.984174\*\* |

| DEV unmatched-FP weight ×4 | 0.979618 | \*\*0.982036\*\* |

| Wrong-branch stress        | 0.983242 | \*\*0.984302\*\* |

| Receiving-twin stress      | 0.977444 | \*\*0.978384\*\* |

| DEV no-true-match          | 0.975234 | \*\*0.985132\*\* |



The reused-CONF paired family-bootstrap interval was approximately:



\*\*\[+0.000861, +0.001079]\*\*



The interval represents sampling variation within the evaluated families and does not correct for validation reuse or the leaderboard distribution gap.



\---



\## 4.6 V3 Rejected Alternative



An alternative approach removed retrieval-context information and attempted to rely more heavily on standalone direct comparison features.



The best standalone DEV score was approximately:



\*\*0.973843\*\*



The best declared 50/50 blend with C4 reached approximately:



\*\*0.982283\*\*



These alternatives did not satisfy the predefined experimental gates and were therefore rejected.



\### Finding



Removing the existing retrieval/model context was not sufficient to improve the overall system.



The selected V3 approach therefore retained C4 as the base and added a specialist only for uncertain cases.



\---



\## 4.7 V3 Test Export



The frozen V3 model was exported to the test candidate set.



Reported export statistics:



\* S1 records: \*\*1,732,544\*\*

\* S1 records with matches: \*\*1,631,363\*\*

\* Matched records: \*\*5,718,652\*\*

\* Match rate: approximately \*\*57.4%\*\*

\* Threshold: \*\*0.80\*\*

\* Baseline blend weight: \*\*0\*\*



The official matching validator passed.



The candidate-pair file remained unchanged.



The V3 test output was not assigned a leaderboard score in the documented experiment.



Therefore, the V3 local DEV score of approximately \*\*0.9842\*\* must not be presented as a leaderboard result.



\---



\# 5. V4 Experiments



\## 5.1 Objective



V4 focused on investigating why the local validation results were substantially higher than the measured leaderboard result.



The starting comparison was:



| Metric         |        Score |

| -------------- | -----------: |

| C4 DEV         |  \*\*0.98322\*\* |

| C4 CONF        |  \*\*0.98321\*\* |

| C4 leaderboard | \*\*0.970441\*\* |



The local DEV and CONF scores were close to each other, suggesting that ordinary validation variance alone did not explain the observed difference.



The V4 analysis therefore investigated possible country-level distribution differences without using test labels.



\---



\# 6. V4 Cross-country Proxy Experiments



\## 6.1 US → India



A model trained only on US data was evaluated on India DEV data.



Reported result:



\*\*0.92951 at threshold 0.80\*\*



For comparison, models with India training information achieved approximately:



\*\*0.9810\*\*



\---



\## 6.2 India → US



A model trained only on India data was evaluated on US DEV data.



Reported result:



\*\*0.94549 at threshold 0.90\*\*



For comparison, models with US training information achieved approximately:



\*\*0.9827\*\*



\---



\## 6.3 Interpretation



These experiments showed that unseen-country transfer could produce a substantial performance reduction in the available labeled proxy setting.



This supported the hypothesis that country-specific distribution differences could contribute to the leaderboard gap.



However, these experiments do \*\*not\*\* directly measure France test accuracy.



\---



\# 7. V4 Self-training Experiments



Self-training was evaluated as a possible way to adapt the model to an unseen country.



Confident predictions were used as pseudo-labels.



\### US → India



The base results were approximately:



| Threshold |    Base | Self-trained |

| --------- | ------: | -----------: |

| 0.70      | 0.92751 |      0.93095 |

| 0.80      | 0.92951 |      0.93300 |

| 0.90      | 0.92749 |  \*\*0.93441\*\* |



\### India → US



| Threshold |    Base | Self-trained |

| --------- | ------: | -----------: |

| 0.70      | 0.94227 |      0.94107 |

| 0.80      | 0.94477 |      0.94313 |

| 0.90      | 0.94549 |      0.94525 |



The common-threshold comparison reported an average improvement from approximately:



\*\*0.93714 → 0.93983\*\*



at the selected comparison threshold.



The effect was positive in one direction and approximately neutral/slightly negative in the other.



Therefore, self-training was treated as promising but not conclusively validated as a universal solution.



\---



\# 8. V4 France-specific Experiments



\## 8.1 France Locale Normalization



A France-specific normalization layer was developed to handle country-specific address and business-name patterns.



The changes included:



\* Region/department normalization

\* French region-code handling

\* `bis` / `ter` normalization

\* `b` / `t` abbreviations

\* `CRS` / `cours` variants

\* Roundabout terminology

\* Apartment tokens

\* Selected legal-form normalization

\* `S.A.` formatting differences



The France records were then re-retrieved and re-featurised.



US and India predictions were kept byte-identical to the original C4 output in the C4-based V4 variants.



\---



\## 8.2 France Self-training



A France-specific pseudo-labeling experiment used:



\* 6.19 million labeled US + India TRAIN rows

\* Approximately 2.21 million France pseudo-labeled rows

\* Approximately 20% of France records as the pseudo-labeled component



The France uncertainty band was reported to decrease approximately from:



\*\*7.2% → 4.3%\*\*



This was used as a diagnostic indicator of the effect of the adaptation.



It was not treated as a direct accuracy measurement.



\---



\## 8.3 France Threshold Experiments



Two main France configurations were retained for consideration:



\### Conservative France adaptation



```text

v4\_c4fr\_t80

```



Uses France-specific normalization with a threshold of:



\*\*0.80\*\*



\### France normalization + self-training



```text

v4\_c4fr\_frp\_t90

```



Uses France-specific normalization and France pseudo-labeling with a threshold of:



\*\*0.90\*\*



Additional variants were also generated, including:



```text

v4\_c4fr\_frp\_t80

v4\_v3fr\_frp\_t80

```



These were later treated as superseded variants.



\---



\# 9. V4 Rejected Experiments



Several V4 approaches were tested and rejected.



| Experiment                                      | Result / Observation                | Decision                     |

| ----------------------------------------------- | ----------------------------------- | ---------------------------- |

| Monotone constraints + stronger regularization  | US→India ≈ 0.92560                  | Rejected                     |

| Per-country quantile normalization              | ≈ 0.91702                           | Rejected                     |

| Dropping scale-dependent features               | ≈ 0.92336                           | Rejected                     |

| Quantile normalization + feature dropping       | ≈ 0.92587                           | Rejected                     |

| Two-round self-training                         | ≈ 0.93108                           | Rejected                     |

| Applying test-like distractor density ×2 to DEV | Only ≈ +0.0003 in optimum threshold | Not used for main adaptation |

| Removing retrieval context in V3                | Best standalone ≈ 0.973843          | Rejected                     |

| 50/50 C4 blend of rejected V3 alternative       | ≈ 0.982283                          | Rejected                     |



The rejected approaches are documented to preserve the experimental history and prevent the final project from presenting only successful experiments.



\---



\# 10. Final Findings



\## 10.1 Main V2 Finding



The strongest V2 improvements came from combining:



1\. Better direct pairwise evidence

2\. More training data

3\. Per-record ranking refinement



Together these produced a local C4 result around:



\*\*0.9832 Macro F0.5\*\*



\---



\## 10.2 Main V3 Finding



Role-aware direct comparison features provided a further local improvement.



The V3 configuration reached approximately:



\*\*0.984226 Macro F0.5 on DEV\*\*



compared with:



\*\*0.983219 for C4\*\*



The improvement was relatively small but consistent across several documented stress and validation settings.



\---



\## 10.3 Main V4 Finding



The V4 investigation suggested that unseen-country distribution differences could be relevant to the leaderboard gap.



Cross-country proxy experiments showed substantial drops when the evaluation country was not represented in training.



France-specific normalization and self-training were therefore investigated as targeted adaptations.



However:



> The actual France test labels were unavailable, so the effectiveness of the France-specific V4 modifications could not be directly measured locally.



\---



\# 11. Results That Must Not Be Misrepresented



The following distinctions are important for the public project documentation.



\### 11.1 0.99609



\*\*0.99609\*\* is a candidate-restricted oracle/diagnostic ceiling.



It is \*\*not\*\* the achieved model score.



\### 11.2 0.984226



\*\*0.984226\*\* is the V3 DEV local validation score.



It is \*\*not\*\* a leaderboard score.



\### 11.3 0.984174



\*\*0.984174\*\* is the reused-CONF V3 result.



It is not an independently sealed final test score.



\### 11.4 0.970441



\*\*0.970441\*\* is the measured leaderboard Macro F0.5 associated with the C4 submission.



This is the only leaderboard result documented in the current experiment reports.



\### 11.5 V4 Candidates



The V4 France-adapted candidate files were generated and validated, but no confirmed leaderboard score was available in the documented experiment.



Therefore, no improvement over \*\*0.970441\*\* should be claimed for V4 until an actual leaderboard result is available.



\---



\# 12. Overall Experimental Conclusion



The experiments demonstrate a progressive development process for business entity resolution:



```text

Baseline

&#x20;  |

&#x20;  v

V2 / C4

Direct Evidence

\+ More Training Data

\+ Per-record Refinement

&#x20;  |

&#x20;  v

V3

Role-aware Direct Features

\+ Specialist LightGBM

&#x20;  |

&#x20;  v

V4

Country Generalization Analysis

\+ France-specific Normalization

\+ France Self-training

```



The strongest locally validated configuration was V3, reaching approximately:



\*\*0.984226 Macro F0.5 on DEV\*\*



while the measured C4 leaderboard result remained:



\*\*0.970441\*\*



The gap between local validation and leaderboard performance motivated the V4 investigation.



The project therefore concludes that:



\* Pairwise direct evidence is highly useful for entity resolution.

\* Increasing training data can improve matching quality.

\* Per-record refinement can improve difficult candidate decisions.

\* Role-aware address features can provide additional local gains.

\* Cross-country generalization can be a significant challenge in entity resolution.

\* France-specific adaptation is technically plausible but requires leaderboard confirmation.

\* Candidate retrieval quality remains an important upper-bound constraint.

\* Diagnostic and local validation scores must not be presented as leaderboard achievements.



The experiments emphasize reproducible methodology, explicit rejection of unsuccessful approaches, and conservative interpretation of results.



