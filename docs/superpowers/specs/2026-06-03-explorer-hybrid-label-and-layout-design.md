# Explorer Hybrid Label And Layout Design

Date: 2026-06-03
Scope: `explorer.html`, `site.js`, `site.css`, `tests/test_explorer_page.py`
Status: Approved for implementation planning

## Goal

Tighten the explanation-first explorer so that it presents team identity assignments honestly and remains visually stable when cards expand inline.

This spec addresses three problems in the current explorer:

1. the sticky control surface visually clips into the card area
2. non-hybrid teams are shown with a second identity label that overstates ambiguity
3. expanding one card stretches the neighboring card and distorts the right-column layout

## Locked Product Decisions

1. The control surface remains sticky beneath the site header.
2. Secondary identity is only surfaced in the explorer when `hybrid_flag` is true.
3. Non-hybrid cards should read as single-identity assignments.
4. The card grid should use independent card heights rather than equal-height rows.
5. This is a frontend-only change; the scorer and generated asset schema remain unchanged.

## Why This Change Is Needed

The current explorer inherited more ambiguity than the scored outputs actually support. Every team payload includes a `secondary_identity`, but the local data shows that many non-hybrid teams have runner-up scores that are functionally negligible. Rendering those cases with a second badge makes the UI look methodologically loose even when the underlying assignment is decisive.

In the current local `MLS 2026` snapshot, only San Jose Earthquakes and Sporting Kansas City are flagged as hybrids. Teams such as Atlanta United FC and Austin FC are currently displayed with second identity labels even though their runner-up scores are negligible. The explorer should reflect that difference.

The layout issue compounds that trust problem. Inline expansion is the right interaction model for this page, but the current grid behavior causes adjacent cards to stretch and makes the open state look broken. The controls bar overlap adds a second visual defect at the top of the same page.

## Approaches Considered

### 1. Frontend-only gating of secondary identity UI

Keep the current scorer output and asset shape, but only show secondary identity in the explorer when `hybrid_flag` is true.

Pros:

- fixes the misleading presentation immediately
- avoids retraining or regenerating assets
- keeps the change local to the explorer

Cons:

- the payload still contains runner-up data for non-hybrids even though the UI no longer surfaces it prominently

### 2. Hide all runner-up semantics for non-hybrids

Remove all secondary-identity references from non-hybrid expanded views as well.

Pros:

- produces the cleanest single-identity story

Cons:

- throws away some useful comparison evidence that can still help explain why the primary identity won

### 3. Change the scorer output contract

Stop emitting usable secondary identity data for non-hybrids.

Pros:

- produces the strongest contract consistency

Cons:

- broadens the scope into model/export behavior
- requires asset regeneration and wider test updates

### Recommendation

Adopt approach 1. The explorer should gate visible secondary identity UI on `hybrid_flag`, while still allowing the non-hybrid expanded state to show the primary rationale and score distribution from existing fields.

## Design

### 1. Identity Semantics

#### Collapsed card behavior

For non-hybrid teams:

- show team name
- show the primary identity badge only
- show the natural-language rationale
- show the expand/collapse control

For hybrid teams:

- show the primary identity badge
- show the secondary identity badge
- show a `Hybrid` badge
- keep the natural-language rationale and expand/collapse control

This makes the card headline match the actual strength of the assignment.

#### Expanded card behavior

For non-hybrid teams:

- keep the primary rationale visible
- show identity score distribution
- show top separating features
- do not show a `Secondary identity` block
- do not show a `Score gap` or `Hybrid margin` summary block framed as if the team sits between two identities

For hybrid teams:

- keep the comparison framing
- show the secondary identity description
- show the hybrid margin summary
- keep the identity score distribution and top separating features

The important distinction is that non-hybrid expanded cards explain why the winner won, while hybrid cards explain why the team meaningfully sits between two identities.

#### Percent display rules

The explorer should stop rendering extreme probabilities with naive fixed-point rounding that implies false certainty or false emptiness.

Display rules:

- use bounded labels such as `>99.9%` for values greater than `0.999`
- use bounded labels such as `<0.1%` for values less than `0.001` and greater than zero
- otherwise use a conventional percent format with one decimal place

This avoids misleading outputs like `100.0%` and `0.0%` for nonzero scores.

### 2. Layout Behavior

#### Sticky controls

The control surface stays sticky beneath the site header, but it must remain part of the normal document flow until it reaches its sticky offset.

Required behavior:

- the controls reserve their own vertical space in the layout
- the card list starts below the controls, not underneath them
- the sticky surface has enough bottom separation that the first row of cards never appears clipped by it
- the sticky state should feel like an anchored toolbar, not a floating overlay obscuring content

#### Independent card heights

The team grid should align cards to the top and allow each card to determine its own height.

Required behavior:

- opening one card only changes that card's height
- neighboring cards remain compact
- extra whitespace under shorter adjacent cards is acceptable
- the expanded panel stays inline within the open card

This is preferable to the current equal-height row behavior, which stretches the neighboring card and makes its label area look broken.

### 3. Rendering And Data Flow

The explorer continues to consume the current generated team payloads. No data regeneration is needed for this change.

Relevant fields:

- `primary_identity`
- `secondary_identity`
- `secondary_identity_description`
- `hybrid_flag`
- `hybrid_margin`
- `identity_scores`
- `assignment_explanation`
- `explanation`

Frontend rendering rules:

- `hybrid_flag` is the gate for visible secondary identity UI
- non-hybrid cards ignore `secondary_identity` for badge and comparison-summary rendering
- hybrid cards reuse existing secondary-identity and hybrid-margin fields
- score distribution rendering remains available for both hybrid and non-hybrid cards
- existing fallback copy for older seasons without rich score details remains intact

### 4. Implementation Boundaries

This change should not:

- modify `src/taxonomy_scorer.py`
- alter hybrid-threshold logic
- regenerate `assets/teams_*.json`
- rewrite methodology copy outside the explorer

The only code changes should be in explorer rendering, explorer styling, and explorer-facing structural tests.

### 5. Error Handling And Compatibility

- If a payload lacks detailed `identity_scores`, keep the current fallback message for older seasons.
- If a payload lacks `assignment_explanation.top_feature_deltas`, keep the current fallback message for missing feature-level details.
- If a payload is non-hybrid but still includes runner-up fields, those fields remain available to the code but are not surfaced as headline identity UI.
- Empty-state and load-error behavior should remain unchanged.

### 6. Verification

#### Manual checks

Verify locally that:

1. the control surface stays sticky while scrolling and does not cover the first row of cards
2. expanding a left-column card does not stretch the right-column card
3. non-hybrid cards show one identity badge only
4. hybrid cards show both identity badges plus the `Hybrid` badge
5. non-hybrid expanded cards omit the secondary-identity comparison block
6. hybrid expanded cards retain the comparison block
7. extreme score values render with bounded labels rather than fake `100.0%` or `0.0%`

#### Automated checks

Add lightweight regression coverage that:

- asserts the explorer JS gates secondary identity UI on `hybrid_flag`
- asserts the explorer JS uses bounded percent-label logic for extreme scores
- asserts the explorer CSS uses top-aligned independent card heights rather than stretch-prone equal-height behavior
- uses small fixture-style examples in test logic for one hybrid case and one non-hybrid case instead of depending on mutable live asset outputs

## Success Criteria

This redesign is successful if:

- the explorer no longer implies dual identity for decisive non-hybrid teams
- hybrid teams still preserve their between-identities explanation
- the sticky controls feel anchored without obscuring content
- inline expansion no longer distorts neighboring cards
- the resulting explorer feels more methodologically defensible and visually stable than the current version
