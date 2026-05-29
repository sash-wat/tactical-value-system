# Phase 1 Taxonomy Review And Naming Cleanup

## Scope
This review covers the frozen `phase1_taxonomy_v1` artifact after the stable-taxonomy rework, with a specific focus on:

- identity naming cleanup
- manual taxonomy review using `2024-2026` scored outputs
- MLS-first coherence checks, followed by cross-league sanity checks

The underlying cluster geometry was not changed in this pass. This was a label-and-semantics review, not a re-discovery run.

## Review Criteria
The review used four gates:

1. The identity name should describe the statistical profile the model is actually capturing.
2. The MLS `2024-2026` teams in each bucket should look like a recognizable school of play, not a random residual bucket.
3. Cross-league usage should be directionally sensible for a stable taxonomy, even if some identities are sparse in MLS.
4. If a bucket failed the coherence check, the next step would be retraining or changing taxonomy constraints rather than forcing a better name.

## Naming Decisions
This pass kept the cluster structure but renamed the weakest labels:

- `Advanced Occupation` -> `Territorial Occupation`
- `Aerial Build-Up` -> `Aerial Progression`
- `Transition Pressure / Passing Progression` -> `Direct Transition`
- `Transition Pressure` -> `Transition Surge`

Unchanged:

- `Possession Control`
- `Disruptive Circulation`
- `Aerial Transition`

## Identity Review

### Possession Control
- Statistical signature:
  - top centroid features: `Possession Volume = 1.27`, `Circulation = 1.19`, `Ball Carrying = 0.45`
  - MLS `2024-2026` mean traits: `attempted_passes_for = 1.70`, `pass_completion_percentage_for = 1.69`, `dribbling = 0.71`
- MLS examples:
  - `2024`: Columbus, Houston, LA Galaxy, Orlando, RSL
  - `2025`: Columbus, Houston, LA Galaxy, San Diego
  - `2026`: Columbus, Inter Miami, LA Galaxy, NYCFC, NYRB
- Cross-league usage:
  - `37` MLS team-seasons
  - `4` NWSL team-seasons
  - `7` USLC team-seasons
  - `3` USL1 team-seasons
- Verdict:
  - keep the name
  - this is the cleanest identity in the taxonomy and is exactly what the model says it is: high-volume, high-completion possession with lower directness

### Territorial Occupation
- Statistical signature:
  - top centroid features: `Advanced Occupation = 1.33`, `Pressing = 0.86`, `Ball Carrying = 0.60`
  - MLS `2024-2026` mean traits: `attempted_passes_for = 1.70`, `pass_completion_percentage_for = 1.66`, `receiving = 1.53`, `dribbling = 1.14`
- MLS examples:
  - `2024`: Inter Miami, NYCFC, Portland
  - `2025`: Inter Miami, LAFC, Nashville, Seattle, Vancouver
  - `2026`: Chicago, Cincinnati, LAFC, Seattle, Vancouver
- Cross-league usage:
  - `13` MLS team-seasons
  - `7` NWSL team-seasons
  - `8` USLC team-seasons
  - `4` USL1 team-seasons
- Verdict:
  - rename from `Advanced Occupation`
  - the old name was too close to a single feature label; the bucket is broader than that
  - this profile is really about living high up the pitch through advanced receiving, carrying, and territorial pressure rather than pure possession for possession's sake

### Disruptive Circulation
- Statistical signature:
  - top centroid features: `Disruption = 0.59`, `Circulation = 0.48`, `Ball Carrying = 0.00`
  - MLS `2024-2026` mean traits: `interrupting = 0.87`, `pass_completion_percentage_for = 0.71`, `claiming = 0.43`
- MLS examples:
  - `2024`: Atlanta, Austin, Chicago, Colorado, DC, Minnesota, NYRB, St. Louis
  - `2025`: Austin, DC, NYCFC, NYRB, Portland, RSL, Toronto
  - `2026`: Montréal, Minnesota, Orlando, Portland, San Jose, Toronto
- Cross-league usage:
  - `33` MLS team-seasons
  - `24` USLC team-seasons
  - `13` USL1 team-seasons
- Verdict:
  - keep the name
  - the bucket is coherent: these are not pure pressing teams and not pure possession teams; they are disruption-first teams that reconnect play well enough to avoid looking like a chaotic direct bucket

### Direct Transition
- Statistical signature:
  - top centroid features: `Verticality = 1.32`, `Pressing = 0.57`, `Passing Progression = 0.19`
  - MLS `2024-2026` mean traits: `receiving = 1.56`, `avg_vertical_distance_for = 0.87`, `passing = 0.79`
- MLS examples:
  - `2025`: Philadelphia
  - `2026`: DC, Philadelphia
- Cross-league usage:
  - `3` MLS team-seasons
  - `9` NWSL team-seasons
  - `16` USLC team-seasons
  - `11` USL1 team-seasons
- Verdict:
  - rename from `Transition Pressure / Passing Progression`
  - the old name described features, not a tactical identity
  - the reviewed teams fit a much clearer story: forward-first, lower-possession teams that win games through direct sequences and assertive pressure

### Aerial Progression
- Statistical signature:
  - top centroid features: `Passing Progression = 0.62`, `Aerial Control = 0.36`, `Pressing = 0.20`
  - MLS `2024-2026` mean traits: `receiving = 2.02`, `passing = 1.24`, `interrupting = 1.01`, `claiming = 0.88`
- MLS examples:
  - `2024`: Philadelphia
  - `2025`: San Jose
- Cross-league usage:
  - `2` MLS team-seasons
  - `6` USLC team-seasons
  - `4` USL1 team-seasons
- Verdict:
  - rename from `Aerial Build-Up`
  - the bucket is usable, but the MLS sample is thin
  - `Build-Up` overstated controlled possession; `Aerial Progression` is closer to what the model actually sees: progressive passing plus aerial control and second-ball play
  - keep as a watchlist identity because MLS coverage is sparse

### Aerial Transition
- Statistical signature:
  - top centroid features: `Aerial Control = 0.67`, `Verticality = 0.13`, `Pressing = 0.06`
- MLS examples:
  - `2026`: FC Dallas
- Cross-league usage:
  - `1` MLS team-season
  - `24` NWSL team-seasons
  - `12` USLC team-seasons
  - `8` USL1 team-seasons
- Verdict:
  - keep the name
  - this is a stable cross-league identity, even though it is barely represented in current MLS seasons
  - the profile is materially different from `Aerial Progression`: less progression passing, less receiving structure, more direct aerial-and-second-ball play

### Transition Surge
- Statistical signature:
  - top centroid features: `Verticality = 3.36`, `Pressing = 2.74`, `Passing Progression = 1.94`
  - extreme negatives in `Possession Volume` and `Circulation`
- MLS examples:
  - none in the `2024-2026` scoring set
- Cross-league usage:
  - no `2024-2026` assignments in the current scored outputs
  - reference-cluster size in the `2020-2023` training window: `5`
- Verdict:
  - rename from `Transition Pressure`
  - keep in `v1`, but mark as the clearest watchlist item in the taxonomy
  - this profile is not incoherent; it is just extremely rare
  - if the next training version still produces a tiny identity with zero forward-scoring usage, it should be merged or constrained away rather than kept as a nominal top-level category

## Overall Review Verdict
The taxonomy passed the coherence test well enough to keep the current frozen geometry.

What changed:

- the weakest model-jargony names were replaced with more tactical names
- team-level outputs now carry identity descriptions alongside labels
- metadata now includes identity definitions for downstream consumers

What did not change:

- the number of identities
- the reference window
- the assignment logic
- the hybrid logic

## League-By-League Verdict

### MLS
- active identities in `2024-2026`: `5`
- strongest buckets:
  - `Possession Control`
  - `Disruptive Circulation`
  - `Territorial Occupation`
- sparse but still coherent:
  - `Direct Transition`
  - `Aerial Progression`
  - `Aerial Transition`
- verdict:
  - passes the review
  - MLS is diverse enough that the taxonomy is not collapsing into two generic styles, and the renamed identities describe the visible buckets more honestly than the old labels did

### NWSL
- active identities in `2024-2026`: `4`
- distribution:
  - `Aerial Transition = 24`
  - `Direct Transition = 9`
  - `Territorial Occupation = 7`
  - `Possession Control = 4`
- verdict:
  - passes the review
  - the league skews more toward the direct and aerial side of the taxonomy, but the activated identities are internally consistent and not obviously mislabeled

### USLC
- active identities in `2024-2026`: `6`
- distribution:
  - `Disruptive Circulation = 24`
  - `Direct Transition = 16`
  - `Aerial Transition = 12`
  - `Territorial Occupation = 8`
  - `Possession Control = 7`
  - `Aerial Progression = 6`
- verdict:
  - passes the review
  - this is the broadest taxonomy-coverage league in the scoring set, which is a good sign for a stable cross-league framework

### USL1
- active identities in `2024-2026`: `6`
- distribution:
  - `Disruptive Circulation = 13`
  - `Direct Transition = 11`
  - `Aerial Transition = 8`
  - `Aerial Progression = 4`
  - `Territorial Occupation = 4`
  - `Possession Control = 3`
- verdict:
  - passes the review
  - the league tilts more direct than MLS, but the identity mix is still interpretable and consistent with a lower-possession environment

## Watchlist For The Next Version

1. `Transition Surge`
   - too rare in the `2024-2026` scoring set to be considered fully validated

2. `Aerial Progression`
   - coherent enough to keep, but still lightly represented in MLS

3. Public documentation
   - the site and docs still need to be updated to use the cleaned identity names and descriptions

## Implementation Outcome
This review resulted in the following repo-side changes:

- updated identity naming and description logic in `scripts/train_taxonomy.py`
- added identity descriptions to scorer outputs in `src/taxonomy_scorer.py`
- added identity definitions to generated metadata in `scripts/generate_assets.py`
- refreshed the frozen artifact and `2024-2026` team assets to use the cleaned names
- regenerated the `2024-2026` tactical cluster plots using the updated identity labels

## Verification
- `pytest -q` passed after the rename cleanup
- reviewed outputs still cover `249` scored team-seasons across `2024-2026`
- hybrid rate remains `0.07228915662650602`
- the MLS `2024-2026` buckets remain spread across multiple identities rather than collapsing into a trivial two-bucket scheme
