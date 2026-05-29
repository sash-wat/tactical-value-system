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
