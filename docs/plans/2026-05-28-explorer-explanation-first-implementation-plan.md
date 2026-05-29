# Explorer Explanation-First Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the explorer's season-by-season 2D plot and view toggle with a summary-plus-card experience that explains team identities through inline rationale and expandable statistical evidence.

**Architecture:** Keep the current static-site architecture and generated JSON assets, but simplify the explorer into a single card-first page. `explorer.html` becomes summary + team-card list only, `site.js` owns inline expansion state and rendering, and `site.css` drops the chart/drawer styles in favor of expandable-card styling.

**Tech Stack:** Static HTML, vanilla JavaScript in `site.js`, shared CSS in `site.css`, pytest for lightweight structural regression checks, local `python -m http.server` for browser verification.

---

## File Map

- Modify: `explorer.html`
  - Remove the chart panel, view toggle, and drawer markup.
  - Add a compact league-season summary block and keep the team-card list as the primary surface.
- Modify: `site.js`
  - Remove chart-view and drawer behavior.
  - Add inline expansion state and render the expanded evidence inside team cards.
  - Keep existing filtering and asset-loading flow.
- Modify: `site.css`
  - Remove chart-frame, toggle-row, and drawer-specific explorer styles.
  - Add expandable-card layout, summary-strip styling, and mobile-safe expanded sections.
- Create: `tests/test_explorer_page.py`
  - Lock the new static explorer structure and prevent the 2D chart controls from reappearing silently.

### Task 1: Add Explorer Structure Regression Tests

**Files:**
- Create: `tests/test_explorer_page.py`
- Test: `tests/test_explorer_page.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_explorer_removes_chart_view_and_drawer_shell():
    html = Path("explorer.html").read_text()

    assert 'data-chart-view' not in html
    assert 'data-view-toggle' not in html
    assert 'data-team-drawer' not in html


def test_explorer_keeps_summary_and_card_list_hooks():
    html = Path("explorer.html").read_text()

    assert 'data-explorer-summary' in html
    assert 'data-identity-summary' in html
    assert 'data-team-grid' in html
    assert 'data-empty' in html


def test_site_js_uses_inline_card_expansion_hooks():
    script = Path("site.js").read_text()

    assert "data-toggle-team" in script
    assert "data-team-panel" in script
    assert "openDrawer(" not in script
    assert "renderChartView(" not in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_explorer_page.py -v`
Expected: FAIL because the current explorer still contains `data-chart-view`, `data-view-toggle`, and drawer logic.

- [ ] **Step 3: Write minimal implementation**

```python
# No production code in this task.
# The failure establishes the exact HTML and JS hooks the rewrite must satisfy.
```

- [ ] **Step 4: Run test to verify it still fails for the expected reasons**

Run: `pytest tests/test_explorer_page.py -v`
Expected: FAIL with assertions pointing at the old chart or drawer markup.

- [ ] **Step 5: Commit**

```bash
git add tests/test_explorer_page.py
git commit -m "test: lock explorer explanation-first structure"
```

### Task 2: Rewrite Explorer Markup and Rendering Flow

**Files:**
- Modify: `explorer.html`
- Modify: `site.js`
- Test: `tests/test_explorer_page.py`

- [ ] **Step 1: Write the failing test for inline expansion hooks**

```python
def test_explorer_exposes_inline_expansion_targets():
    html = Path("explorer.html").read_text()

    assert 'data-team-grid' in html
    assert 'data-identity-summary' in html
    assert 'data-team-drawer' not in html


def test_site_js_renders_expandable_cards_instead_of_drawer():
    script = Path("site.js").read_text()

    assert "renderTeamCards" in script
    assert "data-toggle-team" in script
    assert "assignment_explanation.rationale" in script
    assert "secondary_identity_description" in script
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_explorer_page.py::test_site_js_renders_expandable_cards_instead_of_drawer -v`
Expected: FAIL because the current implementation still uses `data-open-team` and drawer rendering.

- [ ] **Step 3: Write minimal implementation**

Update `explorer.html` so the main explorer content looks like this:

```html
<div class="data-panel reveal">
  <div class="section-header" style="margin-bottom: 1rem;">
    <span class="eyebrow"><i data-lucide="table-properties"></i> Team Cards</span>
    <h3>Primary identity, secondary pull, and team-level explanation</h3>
    <p>Every card keeps the rationale visible and lets you expand inline for the statistical evidence.</p>
  </div>
  <div class="panel" data-identity-summary></div>
  <div class="team-grid" data-team-grid></div>
  <div class="empty-state hidden" data-empty>No teams match the current search and identity filter.</div>
</div>
```

Update `site.js` so inline expansion is stateful inside the card renderer instead of opening a drawer:

```javascript
let expandedTeam = null;

const toggleExpandedTeam = (team) => {
  expandedTeam = expandedTeam === team ? null : team;
  renderTeamCards(currentTeams, currentSearch, activeIdentity, expandedTeam, toggleExpandedTeam);
};

function renderTeamCards(teams, search, activeIdentity, expandedTeam, onToggle) {
  // filter rows first
  // render primary/secondary/hybrid/rationale in collapsed state
  // render identity scores, top features, secondary description, and hybrid margin inline when expanded
}
```

Remove these now-obsolete flows from `site.js`:

```javascript
function renderChartView() {}
function openDrawer() {}
function closeDrawer() {}
```

Also remove the `toggleButtons`, `chartView`, `tableView`, and drawer-close wiring from `initExplorerPage()`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_explorer_page.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add explorer.html site.js tests/test_explorer_page.py
git commit -m "feat: make explorer explanation-first and inline-expandable"
```

### Task 3: Restyle the Explorer Around Summary and Expandable Cards

**Files:**
- Modify: `site.css`
- Modify: `explorer.html`
- Test: `tests/test_explorer_page.py`

- [ ] **Step 1: Write the failing test for removed chart and drawer labels**

```python
def test_explorer_copy_no_longer_mentions_chart_view():
    html = Path("explorer.html").read_text()

    assert "Read the chart" not in html
    assert "move between map and table views" not in html


def test_explorer_styles_no_longer_define_drawer_or_chart_frame():
    css = Path("site.css").read_text()

    assert ".drawer" not in css
    assert ".chart-frame" not in css
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_explorer_page.py::test_explorer_styles_no_longer_define_drawer_or_chart_frame -v`
Expected: FAIL because `site.css` still contains `.drawer` and `.chart-frame`.

- [ ] **Step 3: Write minimal implementation**

Adjust the hero copy in `explorer.html` to remove chart language:

```html
<h1 class="display">Read the identity, then inspect the evidence underneath it.</h1>
<p class="lede">
  Switch league and season, filter identities, and inspect why a team was scored into a particular tactical profile.
</p>
```

Replace the obsolete CSS blocks with expandable-card styles:

```css
.identity-summary-panel {
  margin-bottom: 1rem;
}

.team-card__expand {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.team-card__details {
  display: grid;
  gap: 0.85rem;
  padding-top: 0.9rem;
  border-top: 1px solid rgba(247, 242, 232, 0.08);
}

.team-card__details.hidden {
  display: none;
}
```

Delete the old `.toggle-row`, `.chart-frame`, `.view-grid`, `.drawer`, `.drawer__*`, and score-panel styles that only exist for the removed chart/drawer UI.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_explorer_page.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add explorer.html site.css tests/test_explorer_page.py
git commit -m "style: simplify explorer around summary and expandable cards"
```

### Task 4: End-to-End Verification

**Files:**
- Verify: `explorer.html`
- Verify: `site.js`
- Verify: `site.css`
- Verify: `assets/metadata_mls_2026.json`
- Verify: `assets/teams_mls_2026.json`

- [ ] **Step 1: Run the Python regression tests**

Run: `pytest tests/test_explorer_page.py -v`
Expected: PASS

- [ ] **Step 2: Run broader repo verification**

Run: `pytest -q`
Expected: PASS with the existing Python suite still green.

- [ ] **Step 3: Run a local static server**

Run: `python -m http.server 8000`
Expected: local server starts without errors and serves `/explorer.html`.

- [ ] **Step 4: Verify the explorer manually in a browser**

Check these flows:

```text
1. Open http://127.0.0.1:8000/explorer.html
2. Confirm there is no chart or chart/table toggle.
3. Switch league and season and confirm the identity summary refreshes.
4. Search for a team and confirm the card list filters correctly.
5. Change the identity filter and confirm only matching primary identities remain.
6. Expand one card and confirm rationale, identity scores, top separating features, secondary description, and hybrid margin render inline.
7. Expand a second card and confirm the first one closes if single-open behavior is implemented.
8. Confirm mobile-width layout keeps expanded content readable.
```

- [ ] **Step 5: Commit**

```bash
git add explorer.html site.js site.css tests/test_explorer_page.py
git commit -m "test: verify explanation-first explorer rewrite"
```

## Self-Review

- Spec coverage: the plan removes the 2D plot and view toggle, keeps the compact summary, preserves card-based scanning, makes rationale primary, and moves deeper stats into inline expansion.
- Placeholder scan: each task names exact files, concrete test assertions, commands, expected outcomes, and the specific obsolete hooks that must be removed.
- Type consistency: the plan standardizes on `data-toggle-team`, `data-team-grid`, `data-identity-summary`, `assignment_explanation.rationale`, `assignment_explanation.top_feature_deltas`, and `secondary_identity_description`.
