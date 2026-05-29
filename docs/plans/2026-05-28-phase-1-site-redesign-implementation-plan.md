# Phase 1 Site Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the public site around the stable Phase 1 taxonomy with a new landing page, a methodology page, and a dynamic explorer page that matches the implemented model.

**Architecture:** Keep the site static and asset-driven. Introduce shared frontend assets for layout, palette, navigation, and data-loading, then rewrite the landing page, add `methodology.html` and `explorer.html`, and repoint legacy pages away from stale taxonomy framing.

**Tech Stack:** Static HTML, shared CSS, vanilla JavaScript, existing JSON/PNG assets under `assets/`

---

### Task 1: Shared Frontend Foundation

**Files:**
- Create: `site.css`
- Create: `site.js`
- Test: visual verification across all rewritten pages

- [ ] Define shared CSS variables, typography, layout primitives, buttons, cards, navigation, mobile drawer, data panels, and responsive breakpoints in `site.css`.
- [ ] Add shared JS utilities in `site.js` for mobile navigation, sticky header state, scroll reveals, active section handling, and small formatting helpers.
- [ ] Load the shared CSS and JS from the redesigned pages so the visual system is consistent and future edits do not require duplicating styles in every HTML file.

### Task 2: Landing Page Rewrite

**Files:**
- Modify: `index.html`
- Test: visual verification of hero, snapshot, CTAs, and mobile layout

- [ ] Replace the old homepage copy and structure with the new landing architecture from the spec.
- [ ] Add sections for hero, what changed, taxonomy snapshot, current highlights, why it matters, and entry paths.
- [ ] Pull a small live snapshot from current metadata or team assets so the landing page reflects the frozen taxonomy rather than hard-coded legacy claims.
- [ ] Ensure the page uses the new palette, typography, and scroll-driven interactions.

### Task 3: Methodology Page Build

**Files:**
- Create: `methodology.html`
- Test: visual verification of sticky subnav, content sections, and identity definition rendering

- [ ] Build a methodology page that explains the actual model flow: reference window, feature schema, frozen scoring, primary/secondary identity logic, hybrid logic, explanation layer, validation, and limits.
- [ ] Render the current identity set using the renamed taxonomy and descriptions from metadata.
- [ ] Remove all legacy framing around `PCA-KMeans`, `15 identities`, and yearly rediscovery.

### Task 4: Explorer Page Build

**Files:**
- Create: `explorer.html`
- Test: manual interaction testing for selectors, filters, chart/table toggle, and detail panel

- [ ] Build a dynamic explorer around the existing `assets/teams_*` and `assets/metadata_*` files.
- [ ] Implement league and season selectors, identity filters, team search, and chart/table view toggle.
- [ ] Show primary identity, secondary identity, hybrid status, and explanation summary in the default team listing.
- [ ] Add a team detail drawer or modal with trait scores, identity score breakdown, and top separating features.
- [ ] Display the existing tactical cluster image in chart view with metadata and identity summaries beside it.

### Task 5: Legacy Page Repointing

**Files:**
- Modify: `league-pulse.html`
- Modify: `all-identities.html`
- Modify: `players.html`
- Test: navigation consistency and stale-copy removal

- [ ] Repoint `league-pulse.html` to the new explorer experience or convert it into a compatibility shell that forwards users to `explorer.html`.
- [ ] Repoint `all-identities.html` away from the obsolete “15 identities” story and toward the methodology page.
- [ ] Align `players.html` navigation and top-level styling with the new site system so it feels like part of the same product.

### Task 6: Verification

**Files:**
- Test: `index.html`, `methodology.html`, `explorer.html`, `players.html`, `league-pulse.html`, `all-identities.html`

- [ ] Run a local static server and verify the redesigned pages load.
- [ ] Confirm the explorer fetches current metadata and team assets successfully.
- [ ] Verify responsive behavior on desktop and mobile-sized layouts.
- [ ] Check that stale public claims about `PCA-KMeans`, `15 identities`, and per-season discovery are removed from the main experience.

