from pathlib import Path


def test_explorer_removes_chart_view_and_drawer_shell():
    html = Path("explorer.html").read_text()

    assert "data-chart-view" not in html
    assert "data-table-view" not in html
    assert "data-view-toggle" not in html
    assert "data-team-drawer" not in html


def test_explorer_keeps_summary_and_card_list_hooks():
    html = Path("explorer.html").read_text()

    assert "data-explorer-summary" in html
    assert "data-identity-summary" in html
    assert "data-team-grid" in html
    assert "data-empty" in html


def test_site_js_uses_inline_card_expansion_hooks():
    script = Path("site.js").read_text()

    assert "data-toggle-team" in script
    assert "data-team-panel" in script
    assert "data-open-team" not in script
    assert "openDrawer(" not in script
    assert "renderChartView(" not in script


def test_site_js_guards_against_stale_explorer_refreshes():
    script = Path("site.js").read_text()

    assert "let refreshToken = 0" in script
    assert "const requestToken = ++refreshToken" in script
    assert "if (requestToken !== refreshToken) return;" in script


def test_site_js_handles_legacy_team_payloads_in_expanded_cards():
    script = Path("site.js").read_text()

    assert "info.identity_scores || info.scores || {}" in script
    assert "Detailed identity score distribution is only available for 2024+ scored teams." in script
    assert "Feature-level separation details are only available for 2024+ scored teams." in script


def test_explorer_copy_no_longer_mentions_chart_view():
    html = Path("explorer.html").read_text()

    assert "Read the chart" not in html
    assert "move between map and table views" not in html


def test_explorer_styles_no_longer_define_drawer_or_chart_frame():
    css = Path("site.css").read_text()

    assert ".drawer" not in css
    assert ".chart-frame" not in css


def test_site_js_gates_secondary_identity_ui_on_hybrid_flag():
    script = Path("site.js").read_text()

    assert "function formatExplorerScoreLabel(value)" in script
    assert "const showHybridContext = Boolean(info.hybrid_flag && secondaryIdentity);" in script
    assert 'showHybridContext ? `<span class="badge badge--secondary">${secondaryIdentity}</span>` : ""' in script
    assert 'showHybridContext ? `<span class="badge badge--hybrid">Hybrid</span>` : ""' in script
    assert ">99.9%" in script
    assert "<0.1%" in script


def test_site_css_preserves_sticky_controls_without_translucent_overlap():
    css = Path("site.css").read_text()

    assert ".explorer-controls" in css
    assert "position: sticky;" in css
    assert "backdrop-filter: blur(18px);" in css
    assert "box-shadow: 0 12px 32px rgba(5, 12, 10, 0.22);" in css


def test_site_css_uses_independent_card_heights():
    css = Path("site.css").read_text()

    assert ".team-grid" in css
    assert "align-items: start;" in css
    assert ".team-card" in css
    assert "align-self: start;" in css


