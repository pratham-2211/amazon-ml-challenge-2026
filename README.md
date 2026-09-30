\# Amazon ML Challenge 2026 — Business Entity Resolution



A machine learning project developed for the Amazon ML Challenge 2026 focused on business entity resolution.



The task is to identify whether records from different sources refer to the same real-world business entity. The solution combines candidate generation, direct comparison features, gradient-boosted matching, per-record ranking, and country-aware refinement.



\## Project Overview



Business entity resolution is a record linkage problem where information about the same business may appear differently across multiple datasets.



The project follows a multi-stage pipeline:



Input Business Records

&#x20;       ↓

Data Normalization

&#x20;       ↓

Candidate Generation / Blocking

&#x20;       ↓

Feature Engineering

&#x20;       ↓

LightGBM Matching

&#x20;       ↓

Per-record Ranking

&#x20;       ↓

Role-aware Refinement

&#x20;       ↓

Country-specific Adaptation

&#x20;       ↓

Final Candidate Matches



The implementation was developed through multiple experimental iterations, with V2, V3, and V4 representing successive improvements and analyses.



\## Key Techniques



\- Text and address normalization

\- Candidate generation / blocking

\- IDF-weighted token agreement

\- Name and address similarity features

\- Premise and unit-number comparison

\- Direct raw-text comparison features

\- LightGBM-based pairwise matching

\- Per-record top-candidate refinement

\- Role-aware address feature modeling

\- Cross-country generalization analysis

\- France-specific normalization and pseudo-label adaptation

\- Stress testing and robustness analysis

\- Submission validation and reproducibility checks



\## Experimental Development



\### V2



V2 introduced several improvements over the initial baseline:



\- Removal of a population-dependent feature

\- Direct evidence features for names and addresses

\- Increased training data

\- Per-record second-stage refinement

\- Robustness and stress testing



The final V2 C4 configuration achieved:



\- DEV Macro F0.5: 0.98322

\- CONF Macro F0.5: 0.98321

\- Paired validation improvement over baseline: approximately +0.00533



\### V3



V3 introduced a role-aware refinement stage using direct comparison features such as:



\- Premise and unit roles

\- House-number suffix conflicts

\- Alphabetic address agreement

\- Fuzzy unmatched name/address tokens

\- Raw text agreement

\- Existing C3 confidence features



The specialist model was applied selectively to uncertain C3 predictions.



Measured local validation:



\- DEV Macro F0.5: 0.984226

\- Reused CONF Macro F0.5: 0.984174

\- Selected threshold: 0.80



The V3 test export was successfully validated using the official submission validator.



\### V4



V4 investigated the gap between local validation and the measured challenge leaderboard result, with particular attention to cross-country generalization.



The analysis identified France as a distinct test-time challenge because the country had no corresponding training data.



The France-specific experiments included:



\- French-locale normalization

\- Region and department normalization

\- Address abbreviation handling

\- Legal-form normalization

\- France-specific pseudo-label adaptation

\- Threshold experiments for unseen-country conditions



These experiments were treated as candidate improvements and were not presented as measured leaderboard gains without confirmation.



\## Results



\### Local Validation



| Experiment | DEV Macro F0.5 | CONF Macro F0.5 |

|---|---:|---:|

| V2 C4 | 0.98322 | 0.98321 |

| V3 Role-aware | 0.984226 | 0.984174 |



\### Challenge Leaderboard



The measured leaderboard score for the submitted C4 configuration was:



\*\*Macro F0.5: 0.970441\*\*



This is the externally measured challenge result and is kept separate from local validation scores.



\### Diagnostic Ceiling



A candidate-restricted oracle achieved:



\*\*0.99609 Macro F0.5\*\*



This is a diagnostic retrieval ceiling, not the performance of the trained matching model.



\## Important Result Distinction



The project intentionally distinguishes between:



\- 0.970441 — measured C4 challenge leaderboard score

\- \~0.984 — local validation performance of later experimental variants

\- 0.99609 — candidate-restricted diagnostic oracle ceiling



The diagnostic ceiling and local validation results should not be interpreted as the final challenge leaderboard score.



\## Reproducibility and Validation



The project includes:



\- Deterministic training configurations

\- Data and configuration fingerprints

\- Atomic output generation

\- Checkpointing and recovery mechanisms

\- Submission validation

\- Candidate-subset validation

\- Reproducibility checks

\- Stress testing



The repository contains the reusable source code and documentation required to understand the methodology.



Raw challenge datasets, large candidate files, local databases, caches, and generated submission artifacts are intentionally excluded from the repository.



\## Repository Structure



AMAZON-ML-CHALLENGE-2026/

│

├── README.md

├── requirements.txt

├── .gitignore

│

├── src/

│   ├── train\_v2.py

│   ├── predict\_v2.py

│   ├── scorer.py

│   │

│   ├── experiments/

│   │   ├── v3/

│   │   │   ├── train.py

│   │   │   ├── direct\_features.py

│   │   │   └── blend\_sweep.py

│   │   │

│   │   └── v4/

│   │       └── v3fr.py

│   │

│   └── utils/

│       └── validate\_submission.py

│

├── docs/

│   ├── methodology.md

│   ├── experiments.md

│   ├── results.md

│   ├── problem\_statement.md

│   ├── original\_project\_readme.md

│   └── documentation\_template.md

│

├── notebooks/

├── configs/

└── results/

&#x20;   └── figures/



\## Documentation



Detailed technical information is available in:



\- docs/problem\_statement.md — problem definition and task context

\- docs/methodology.md — complete methodology and evaluation approach

\- docs/experiments.md — experiment history, comparisons, and rejected approaches

\- docs/results.md — consolidated results and limitations



\## Limitations



The reported results have important scope limitations:



\- The challenge leaderboard result refers specifically to the submitted C4 configuration.

\- Later V3/V4 variants were primarily evaluated through local experiments.

\- V3 reused the existing CONF split from the earlier experimental framework.

\- France-specific accuracy was not independently measured with labeled France ground truth.

\- Cross-country experiments are treated as generalization diagnostics rather than direct leaderboard measurements.

\- The candidate-restricted oracle is a diagnostic ceiling, not a deployable model.



\## Disclaimer



This repository is a personal technical showcase of work developed for the Amazon ML Challenge 2026.



It does not contain proprietary Amazon data, confidential challenge infrastructure, or large raw challenge datasets.



The repository documents the methodology, experiments, implementation structure, and measured results without claiming Amazon endorsement, selection, or employment.



\## Author



Pratham Chaturvedi



B.Tech — Computer Science \& Engineering



PSIT Kanpur

