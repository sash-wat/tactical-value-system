# Phase 1 Site Redesign Spec

## Objective
Rebuild the public website around the new Phase 1 stable taxonomy so the site matches the actual methodology and presents it as a coherent product.

The new site should:

- replace the old `PCA-KMeans` / `15 identities` / exploratory-clustering story
- lead with a strong landing page
- include a dedicated methodology page
- include a dynamic explorer page for tables and graphs
- remain responsive and interactive on desktop and mobile
- use a more intentional visual system than the current blue-purple glass style

## Product Scope
The redesigned core site has three primary pages:

1. `index.html`
   Landing page with highlights, narrative framing, and calls to action.

2. `methodology.html`
   Dedicated explanation of the stable taxonomy and what the model actually does.

3. `explorer.html`
   Interactive team explorer for plots, tables, identity filters, and team-level explanations.

Secondary page:

4. `players.html`
   Kept available, but treated as a secondary destination rather than one of the core Phase 1 pages.

Legacy pages to retire or repurpose:

- `all-identities.html`
  Replace with `methodology.html`. Do not preserve the old “The 15 Identities” framing.

- `league-pulse.html`
  Replace with `explorer.html`. The current dynamic image/table loading can be reused conceptually, but the page should be redesigned rather than lightly edited.

## Core Narrative
The site should communicate three things clearly:

1. What TVMS Phase 1 is
   A stable taxonomy for classifying team playing styles across leagues and seasons.

2. Why it is credible
   It is trained on a frozen `2020-2023` reference cohort and scores `2024+` teams against the same model.

3. How to use it
   Users can read the methodology, then inspect league-season outputs in the explorer.

The landing page should summarize. The methodology page should prove. The explorer should let users interrogate the outputs.

## Information Architecture

### Navigation
Primary nav:

- `Home`
- `Methodology`
- `Explorer`

Secondary nav or utility link:

- `Players`
- `GitHub`

Navigation behavior:

- sticky header
- compact state after scroll
- active-page indication
- mobile drawer on small screens

### Footer
Footer should include:

- brief product descriptor
- data source attribution to American Soccer Analysis
- GitHub link
- optional link to `Players`

## Visual Direction
The site should move away from the current generic dark-glass aesthetic.

### Mood
Target feel:

- editorial
- analytical
- modern club strategy desk
- premium but restrained

Avoid:

- purple-heavy SaaS gradients
- default-looking dashboard chrome
- decorative floating effects that do not help structure

### Palette
Use a warmer, more grounded palette:

- background light: warm ivory / parchment
- background dark: deep forest / near-black green
- accent 1: oxidized teal
- accent 2: brass / muted gold
- accent 3: rust / clay
- neutral text: charcoal / off-white

The explorer may use darker data panels for contrast, but the overall site should not collapse back into the current blue-purple look.

### Typography
Use a higher-contrast type system:

- serif display face for major headings
- sharper sans-serif for body and UI
- monospace only for metadata, labels, and diagnostics

The typography should carry more of the site’s personality than the current implementation.

### Surfaces
Prefer:

- paper-like panels
- thin rules
- subtle texture or gradients
- restrained shadows
- occasional dark inset panels for charts/tables

## Page Requirements

### 1. Landing Page
Purpose:

- introduce the new taxonomy
- make the redesign feel intentional and modern
- direct users into methodology and explorer flows

Sections:

1. Hero
   Clear thesis, short supporting paragraph, and two CTAs:
   - `Open Explorer`
   - `Read Methodology`

2. What Changed
   Explain that the old per-season clustering story has been replaced by a frozen reference taxonomy.

3. Taxonomy Snapshot
   Present the current stable identities as a concise visual system, not as long text blocks.

4. Current Highlights
   Show a small live snapshot drawn from current assets:
   - number of identities
   - reference window
   - scoring window
   - current hybrid rate or other validation metric

5. Why It Matters
   Explain why comparing team styles across leagues and years is useful.

6. Entry Paths
   Two clear routes:
   - methodology for explanation
   - explorer for data interaction

Behavior:

- staggered reveal on scroll
- sticky header state change
- active section indicator if useful
- cards or highlight strips that respond to hover/focus

### 2. Methodology Page
Purpose:

- replace the stale taxonomy page with an honest explanation of the implemented model

Sections:

1. Model Summary
   Short explanation of what the taxonomy does.

2. Reference Window
   Explain `2020-2023` training and `2024+` scoring.

3. Feature Schema
   Explain the fixed tactical feature set actually used in Phase 1.

4. Identity Discovery And Frozen Scoring
   Explain that clustering is used to define the taxonomy on the reference cohort, then future teams are scored against the frozen model.

5. Primary, Secondary, And Hybrid Logic
   Explain primary identity, secondary identity, and hybrid handling.

6. Statistical Explanation Layer
   Explain how assignments are justified with feature-level evidence.

7. Validation And Limits
   Explain what was validated and what remains a watchlist item.

8. Current Identity Set
   Present the current stable identity names with short descriptions.

Behavior:

- sticky subnav or progress rail
- expandable sections for deeper detail if needed
- scannable diagrams or process strips

Content rules:

- no `PCA-KMeans` language
- no `15 identities` language
- no claim that labels are discovered independently each season

### 3. Explorer Page
Purpose:

- become the main interactive data workspace for Phase 1 outputs

Main capabilities:

- choose league
- choose season
- switch between chart and table modes
- filter by identity
- inspect team-level explanation
- see primary and secondary identity together

Controls:

- league selector
- season selector
- identity filters
- chart/table toggle
- optional search box for team name

Views:

1. Chart view
   Display the existing tactical cluster image for the selected league/season.
   Supplement it with identity summary chips and metadata.

2. Table/card view
   Show teams with:
   - team name
   - primary identity
   - secondary identity
   - hybrid marker
   - short explanation
   - trait or score highlights

3. Team detail drawer or modal
   On click, show:
   - full explanation
   - trait scores
   - identity score distribution
   - top separating features

Data sources:

- continue using generated assets under `assets/`
- use team JSON and metadata JSON as the main frontend data sources
- no need to introduce a backend

Responsive behavior:

- sticky controls on desktop
- collapsible controls on mobile
- chart/table toggle remains easy to use on small screens
- detail drawer becomes stacked modal or in-flow expansion on mobile

## Motion And Interaction
Motion should explain structure, not decorate emptiness.

Use:

- sticky-header transition on scroll
- section reveal choreography
- active filter states
- animated chart/table toggle
- smooth expansion for team detail panels
- subtle loading states when assets change

Avoid:

- idle floating blobs
- gratuitous glow pulses
- animations unrelated to navigation or data interaction

## Content Alignment Rules
The site must align with the actual Phase 1 implementation.

Explicitly remove or rewrite:

- all references to `15 identities`
- all references to `PCA-KMeans`
- all references to exploratory yearly clustering as the main public story
- stale identity names replaced by the current taxonomy review

The site should use the current renamed identity set:

- `Possession Control`
- `Territorial Occupation`
- `Disruptive Circulation`
- `Direct Transition`
- `Aerial Progression`
- `Aerial Transition`
- `Transition Surge`

The methodology page should also note that some identities are watchlist categories if they are sparse in current MLS scoring usage.

## Implementation Boundaries
This redesign should remain a static site built from the existing HTML-and-assets workflow.

Allowed:

- shared CSS variables and shared JS utilities
- shared navigation/footer patterns
- light client-side rendering from existing JSON assets
- reusing parts of current `league-pulse.html` data loading behavior

Not required:

- framework migration
- backend
- build tooling change

If a shared stylesheet or shared JS file materially improves maintainability, it should be introduced.

## Success Criteria
The redesign is complete when:

1. The site has three coherent primary pages:
   - landing
   - methodology
   - explorer

2. The public story matches the implemented stable taxonomy.

3. The explorer is interactive and clearly more useful than the current `league-pulse.html`.

4. The site is visually distinct from the current blue-purple glass treatment.

5. The pages are responsive on desktop and mobile.

6. The navigation and scrolling behavior feel deliberate and dynamic.

7. The old stale taxonomy framing is no longer exposed as the main public experience.

## Proposed File Changes
Likely file plan:

- `index.html`
  full rewrite

- `methodology.html`
  new file

- `explorer.html`
  new file replacing `league-pulse.html` as the primary data page

- `league-pulse.html`
  either redirect-like shell, compatibility page, or light alias to explorer

- `all-identities.html`
  retire or repoint away from the old framing

- `players.html`
  nav and styling alignment pass only, unless deeper issues surface

- shared assets:
  - optional `site.css`
  - optional `site.js`

## Review Notes
This spec intentionally prioritizes:

- methodological honesty
- stronger visual authorship
- a cleaner public product narrative

It does not yet prescribe exact copy, exact fonts, or exact HTML structure. Those should be finalized during implementation while preserving the architecture and alignment rules above.
