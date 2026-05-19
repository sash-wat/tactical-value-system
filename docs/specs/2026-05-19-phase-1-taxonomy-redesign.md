# Phase 1 Taxonomy Redesign Handoff

**Date:** 2026-05-19  
**Status:** Design locked for handoff  
**Scope:** Team classification methodology for TVMS Phase 1

## Objective

Redesign TVMS Phase 1 so that it produces a **stable tactical taxonomy** for teams across leagues and seasons rather than a per-season exploratory clustering result.

The new Phase 1 output should assign each team:

- a `primary_identity`
- a `secondary_identity`
- full `identity_scores` across the taxonomy
- a `hybrid_flag` when the top two identities are close enough to justify a between-identities reading
- trait-level standardized scores
- a statistical explanation of why the assignment was made

The system should be explainable, versioned, and comparable across time.

## Locked Design Decisions

### 1. Stable Taxonomy, Not Season-By-Season Refitting

Phase 1 is no longer a league-season-specific clustering exercise. It should become a stable classification system that can be used to compare teams across leagues and across seasons.

### 2. Reference Window And Scoring Window

- **Reference cohort:** `2020-2023`
- **Scoring set:** `2024+`

The taxonomy should be learned from the pooled `2020-2023` reference cohort and then frozen. Teams from `2024+` should be scored against that fixed model rather than causing the taxonomy to be refit each year.

### 3. Taxonomy Size

The final taxonomy should contain **5-7 primary identities**.

There is **no requirement to preserve the existing 15 preset identities**. Identity count and naming should be driven by what the reference data can support consistently.

### 4. Output Shape

Each scored team should receive:

- `primary_identity`
- `secondary_identity`
- `identity_scores`
- `hybrid_flag`
- `trait_scores`
- `assignment_explanation`

This replaces the current single-label-only framing.

## Model Architecture

The redesigned Phase 1 system should be split into explicit components.

### 1. Feature Schema

Define a fixed and audited feature set used for both reference training and future scoring.

Requirements:

- features must be available across MLS, USLC, NWSL, and USL1
- features must be stable across `2020+`
- features must represent tactical profile rather than accidental noise
- the schema must be versioned and documented

The feature set does not need to match the old marketed 15-identity structure.

### 2. Reference Normalizer

Fit scaling and normalization only on the `2020-2023` reference cohort.

Requirements:

- store the fitted normalizer as part of the frozen model artifact
- apply the exact same normalizer to all `2024+` teams
- do not recompute league-season-specific standardization for scoring seasons

This is required for time comparability.

### 3. Identity Discovery Layer

Use the `2020-2023` reference cohort to discover candidate tactical schools of play.

Requirements:

- clustering is allowed only in this discovery phase
- discovery results should be reviewed and consolidated into a stable `5-7` identity taxonomy
- identity definitions should reflect multi-feature profile shape, not a single standout metric

This is the only stage where exploratory modeling belongs.

### 4. Frozen Scoring Model

After the identity set is finalized, freeze the scoring logic into a versioned artifact.

That artifact should include at minimum:

- feature schema version
- fitted normalizer
- frozen identity definitions
- identity centroids, prototypes, or equivalent scoring references
- assignment logic
- hybrid/near-split thresholds
- model version metadata

Example version name:

- `phase1_taxonomy_v1`

### 5. Inference Layer

Score `2024+` teams against the frozen taxonomy.

For every team, the inference layer should output:

- top identity
- second-best identity
- full score vector across all identities
- hybrid status when the top two identities are close
- trait profile
- explanation payload

## Identity Semantics

Identity names should be derived from the final stable taxonomy, not from prewritten marketing copy.

Requirements:

- names should describe repeatable tactical profiles
- names should be understandable to a soccer-literate reader
- names should not imply a single-metric outlier if the model is actually using multi-feature shape
- two teams can share a primary identity while still differing materially in their trait profile

The taxonomy should preserve nuance by combining discrete identity assignment with continuous trait scores.

## Borderline And Hybrid Handling

“Borderline” is **not** an acceptable terminal answer.

If a team sits near the boundary between two identities, the model should still produce a decisive structured output. The correct behavior is to treat that team as a meaningful overlap case, not as an unresolved ambiguity.

Required behavior:

- always assign a `primary_identity`
- always expose a `secondary_identity`
- mark a `hybrid_flag` when the top two identities are sufficiently close
- include the score gap between first and second identity
- support downstream language such as:
  - “primarily X, with a strong secondary fit to Y”
  - “hybrid between X and Y”

This allows the taxonomy to remain decisive without hiding mixed-profile teams.

## Statistical Explanation Requirements

Every assignment should be explainable with statistics.

The system should be able to answer:

- why did this team receive its primary identity?
- which traits most pulled it toward that identity?
- how does its feature profile compare to the frozen identity profile?
- why did identity A beat identity B?
- how large was the gap between first and second identity?

Desired explanation payload for each team:

- top contributing features for the winning identity
- standardized feature values for the team
- identity-level reference values for comparison
- margin between top two identity scores
- a short generated rationale grounded in those values

Example explanation pattern:

> Team X is classified as `Possession Dominant` because its possession volume and pass completion are both well above the frozen reference mean, and those values place it closer to the possession profile than to the next-best direct-attacking profile.

## Validation Requirements

Validation is part of the methodology and should be implemented explicitly.

### 1. Temporal Stability

Check that identities learned on `2020-2023` still produce coherent assignments on `2024+`.

### 2. League Coverage

Check that the taxonomy is not accidentally encoding league membership unless that result is explicitly intended and documented.

### 3. Identity Coherence

Each identity should have a defensible multi-metric profile that can be described clearly.

### 4. Assignment Confidence

Borderline cases should be represented through structured hybrid outputs rather than hidden or dropped.

### 5. Drift Monitoring

The system should be able to detect when newly scored teams are consistently falling far from the frozen taxonomy, which would justify a future taxonomy version.

## Governance And Versioning

The taxonomy must be versioned.

Requirements:

- no silent changes to identity definitions
- no silent changes to feature schema
- no silent changes to normalizer or thresholds
- new taxonomy training windows should produce a new version rather than overwrite the old one

Example:

- `phase1_taxonomy_v1`: trained on `2020-2023`, scored on `2024+`

## Documentation And Product Changes

All public-facing copy and project docs should reflect the actual methodology.

Required changes:

- remove outdated `PCA-KMeans` descriptions unless the final implementation truly uses that method
- remove the claim that Phase 1 is based on 15 preset identities unless that is materially true
- clearly distinguish `reference training window` from `scoring seasons`
- describe outputs as `primary identity + secondary identity + trait profile`
- explain hybrid cases explicitly
- explain that assignments are grounded in frozen reference statistics

## Problems This Redesign Is Intended To Fix

The redesign is specifically intended to correct the following issues in the current scheme:

- labels changing meaning across league-seasons
- public methodology not matching implementation
- cluster labels being overstated as team-level facts
- identities advertised that are not actually reachable from the model
- lack of comparability across years
- inability to explain why a team received a label
- weak handling of teams that sit between profiles

## Handoff Guidance For The Next Model

The next model should treat the following as already decided:

- Phase 1 should produce a stable taxonomy
- the reference cohort is `2020-2023`
- scoring begins at `2024+`
- the taxonomy should have `5-7` identities
- teams should get a primary and secondary identity
- hybrid cases must be represented explicitly
- every assignment must be statistically explainable
- the old 15 preset identities do not need to be preserved

The next step is to turn this design into either:

- a formal implementation spec with concrete component boundaries and artifact definitions, or
- a detailed implementation plan with file-level tasks and tests

