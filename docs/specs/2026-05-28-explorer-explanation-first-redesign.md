# Explorer Explanation-First Redesign

Date: 2026-05-28
Scope: `explorer.html`, `site.js`, `site.css`
Status: Proposed

## Goal

Replace the season-by-season 2D tactical map with an explanation-first explorer that presents team identities through readable team cards and expandable statistical evidence.

The current map view implies geometric meaning that the Phase 1 taxonomy does not support strongly enough. The new explorer should explain classification decisions directly rather than asking users to infer them from a 2D projection.

## Locked Product Decisions

1. Remove the season-by-season 2D plot from the explorer.
2. Remove the chart/table toggle entirely.
3. Keep a compact league-season summary above the team list.
4. Keep the main explorer surface card-based rather than converting it to a dense table.
5. Make the plain-language rationale the primary explanation shown on every team card.
6. Let users expand a card inline to inspect the deeper statistical evidence.

## Page Structure

The explorer page will have three layers:

### 1. Control Bar

The top control surface remains:

- league selector
- season selector
- team search
- identity filter

The current view toggle is removed.

### 2. League-Season Summary

Directly under the controls, the page shows a compact non-spatial summary for the selected league-season:

- league and season label
- number of active identities in the selection
- hybrid-team count
- frozen reference-window note
- identity distribution counts

This summary provides context without implying spatial precision or cluster geometry.

### 3. Team Card List

The primary content area is a vertical list of team cards. Each card should be easy to scan in the collapsed state and evidence-rich in the expanded state.

## Team Card Design

### Collapsed State

Each team card shows:

- team name
- primary identity
- secondary identity
- hybrid badge when applicable
- plain-language rationale sentence
- clear expand control

The collapsed card should answer: "What is this team, and why do we think that?"

### Expanded State

Expanding a card reveals the deeper statistical explanation inline. The expanded content includes:

- identity score distribution
- top separating features
- secondary identity description
- score gap or hybrid margin

This should reuse the existing scored data fields where possible rather than inventing a new explanation format.

## Data Contract

The redesign should continue to consume the current generated team payloads. The relevant fields already exist in the scored assets:

- `primary_identity`
- `secondary_identity`
- `secondary_identity_description`
- `hybrid_flag`
- `hybrid_margin`
- `identity_scores`
- `assignment_explanation.rationale`
- `assignment_explanation.top_feature_deltas`

No taxonomy or asset-schema redesign is required for this frontend change.

## Interaction Model

- Search and identity filter apply to the visible card list.
- Expansion is inline on the card, not a separate drawer.
- Only one expanded card needs to be open at a time.
- On mobile, expanded content stacks vertically and keeps the rationale visible near the top.

Inline expansion is preferred over the current drawer because it keeps users anchored in the list and makes team-to-team comparison easier.

## Content Rules

- Do not refer to the removed 2D chart as a map, cluster field, or projection anywhere in the explorer.
- Keep the rationale sentence in plain language, not raw metric jargon.
- Use the expanded section for statistical proof, not for duplicate marketing copy.
- Do not expose internal artifact labels like `phase1_taxonomy_v1` in the main explorer UI.

## Implementation Boundaries

This redesign is limited to the explorer interface. It should not:

- retrain the taxonomy
- change the scored team payload structure
- alter methodology copy outside the explorer unless needed for link or label consistency

## Verification

The implementation should be verified by:

1. loading the explorer locally
2. switching leagues and seasons
3. filtering by identity
4. searching for teams
5. expanding and collapsing cards
6. confirming the rationale and deeper evidence render correctly from live asset data
7. confirming the old 2D chart and view toggle are gone

## Success Criteria

The redesign is successful if:

- the explorer no longer depends on the 2D tactical plot
- every visible team has an immediately readable rationale
- deeper statistical evidence is one click away on the same card
- the page still feels scannable at league-season level
- the UI explains the classification more honestly than the removed chart did
