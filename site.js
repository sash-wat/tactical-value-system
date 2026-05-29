const TVMS_SITE = (() => {
  const DEFAULT_LEAGUE = "mls";
  const DEFAULT_SEASON = "2026";
  const LEAGUES = ["mls", "uslc", "nwsl", "usl1"];
  const SEASONS = ["2026", "2025", "2024", "2023", "2022", "2021", "2020"];

  const titleCaseLeague = (league) => {
    const labels = {
      mls: "MLS",
      uslc: "USL Championship",
      nwsl: "NWSL",
      usl1: "USL League One",
    };
    return labels[league] || league.toUpperCase();
  };

  const formatPercent = (value, digits = 1) => `${(value * 100).toFixed(digits)}%`;
  const formatNumber = (value, digits = 2) => Number(value).toFixed(digits);
  async function fetchJson(path) {
    const response = await fetch(`${path}?v=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${path}: ${response.status}`);
    }
    return response.json();
  }

  function initIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  function initNav() {
    const header = document.querySelector(".site-header");
    const toggle = document.querySelector("[data-mobile-toggle]");
    const mobileNav = document.querySelector("[data-mobile-nav]");

    if (toggle && mobileNav) {
      toggle.addEventListener("click", () => {
        const isOpen = mobileNav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      });
    }

    const onScroll = () => {
      if (!header) return;
      header.classList.toggle("is-scrolled", window.scrollY > 16);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function initReveal() {
    const reveals = document.querySelectorAll(".reveal");
    if (!reveals.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.14 }
    );

    reveals.forEach((item) => observer.observe(item));
  }

  function initMethodNav() {
    const navLinks = Array.from(document.querySelectorAll("[data-method-link]"));
    const sections = navLinks
      .map((link) => document.querySelector(link.getAttribute("href")))
      .filter(Boolean);

    if (!navLinks.length || !sections.length) return;

    const sync = () => {
      const anchor = window.scrollY + 160;
      let activeId = sections[0].id;
      sections.forEach((section) => {
        if (section.offsetTop <= anchor) {
          activeId = section.id;
        }
      });
      navLinks.forEach((link) => {
        const target = link.getAttribute("href").slice(1);
        link.classList.toggle("is-active", target === activeId);
      });
    };

    sync();
    window.addEventListener("scroll", sync, { passive: true });
  }

  async function loadLatestMetadata(preferredLeague = DEFAULT_LEAGUE) {
    for (const season of SEASONS) {
      try {
        const [metadata, teams] = await Promise.all([
          fetchJson(`assets/metadata_${preferredLeague}_${season}.json`),
          fetchJson(`assets/teams_${preferredLeague}_${season}.json`),
        ]);
        return { metadata, teams, league: preferredLeague, season };
      } catch (_error) {
        continue;
      }
    }
    throw new Error("No metadata could be loaded for the preferred league");
  }

  function renderLandingStats({ metadata, teams, league, season }) {
    const statsRoot = document.querySelector("[data-landing-stats]");
    const spotlightRoot = document.querySelector("[data-landing-spotlight]");
    const taxonomyRoot = document.querySelector("[data-landing-identities]");
    if (!statsRoot || !spotlightRoot || !taxonomyRoot) return;

    const teamRows = Object.entries(teams);
    const hybridRate =
      teamRows.filter(([, info]) => Boolean(info.hybrid_flag)).length / Math.max(teamRows.length, 1);

    statsRoot.innerHTML = `
      <div class="metric">
        <div class="metric__label">Reference Window</div>
        <div class="metric__value">${metadata.reference_window.season_start}-${metadata.reference_window.season_end}</div>
      </div>
      <div class="metric">
        <div class="metric__label">Scoring View</div>
        <div class="metric__value">${titleCaseLeague(league)} ${season}</div>
      </div>
      <div class="metric">
        <div class="metric__label">Identity Count</div>
        <div class="metric__value">${metadata.n_clusters}</div>
      </div>
      <div class="metric">
        <div class="metric__label">Hybrid Rate</div>
        <div class="metric__value">${formatPercent(hybridRate, 1)}</div>
      </div>
    `;

    const strongestTeams = teamRows
      .map(([team, info]) => ({
        team,
        primary: info.primary_identity,
        secondary: info.secondary_identity,
        margin: info.hybrid_margin,
      }))
      .sort((left, right) => right.margin - left.margin)
      .slice(0, 4);

    spotlightRoot.innerHTML = strongestTeams
      .map(
        (team) => `
          <div class="hero-panel__item">
            <div>
              <strong>${team.team}</strong>
              <span>${team.primary}${team.secondary ? ` · ${team.secondary} secondary` : ""}</span>
            </div>
            <div class="hero-panel__value">${formatPercent(team.margin, 0)}</div>
          </div>
        `
      )
      .join("");

    taxonomyRoot.innerHTML = Object.entries(metadata.identity_definitions)
      .slice(0, 6)
      .map(
        ([name, info]) => `
          <article class="card identity-card reveal">
            <span class="identity-card__tag">Stable Identity</span>
            <h3>${name}</h3>
            <p>${info.description}</p>
          </article>
        `
      )
      .join("");
    initIcons();
    initReveal();
  }

  async function initLandingPage() {
    try {
      const latest = await loadLatestMetadata();
      renderLandingStats(latest);
    } catch (error) {
      console.error(error);
    }
  }

  async function initMethodologyPage() {
    initMethodNav();
    const identityRoot = document.querySelector("[data-method-identities]");
    const summaryRoot = document.querySelector("[data-method-summary]");
    if (!identityRoot || !summaryRoot) return;

    try {
      const { metadata, league, season } = await loadLatestMetadata();
      summaryRoot.innerHTML = `
        <div class="metric">
          <div class="metric__label">Current Model</div>
          <div class="metric__value">Stable taxonomy</div>
        </div>
        <div class="metric">
          <div class="metric__label">Feature Schema</div>
          <div class="metric__value">${metadata.features.length}</div>
        </div>
        <div class="metric">
          <div class="metric__label">Current View</div>
          <div class="metric__value">${titleCaseLeague(league)} ${season}</div>
        </div>
        <div class="metric">
          <div class="metric__label">Reference Cohort</div>
          <div class="metric__value">${metadata.training_summary.n_team_seasons}</div>
        </div>
      `;

      identityRoot.innerHTML = Object.entries(metadata.identity_definitions)
        .map(
          ([name, info]) => `
            <article class="card">
              <span class="identity-card__tag">Stable Identity</span>
              <h3>${name}</h3>
              <p>${info.description}</p>
              <div class="pill-row" style="margin-top: 0.85rem;">
                ${info.top_features
                  .map((feature) => `<span class="pill">${feature.feature_label}</span>`)
                  .join("")}
              </div>
            </article>
          `
        )
        .join("");
      initIcons();
    } catch (error) {
      console.error(error);
    }
  }

  function renderExplorerMeta(metadata, league, season, teams) {
    const root = document.querySelector("[data-explorer-summary]");
    if (!root) return;
    const hybrids = Object.values(teams).filter((info) => Boolean(info.hybrid_flag)).length;
    root.innerHTML = `
      <strong>${titleCaseLeague(league)} ${season}</strong>
      shows <strong>${metadata.n_clusters} identities</strong>,
      <strong>${hybrids} hybrid teams</strong>,
      and a <strong>${metadata.reference_window.season_start}-${metadata.reference_window.season_end}</strong> reference window.
    `;
  }

  function renderExplorerSummary(metadata, teams) {
    const root = document.querySelector("[data-identity-summary]");
    if (!root) return;
    const counts = Object.values(teams).reduce((acc, team) => {
      acc[team.primary_identity] = (acc[team.primary_identity] || 0) + 1;
      return acc;
    }, {});
    root.innerHTML = Object.entries(metadata.identity_definitions)
      .map(([name, info]) => {
        const count = counts[name] || 0;
        return `
          <div class="summary-item">
            <strong>${name}</strong>
            <div class="team-card__meta">${count} teams · ${info.description}</div>
          </div>
        `;
      })
      .join("");
  }

  function renderIdentityFilters(teams, activeIdentity, onChange) {
    const root = document.querySelector("[data-identity-select]");
    if (!root) return;
    const identities = ["All", ...new Set(Object.values(teams).map((item) => item.primary_identity))];
    root.innerHTML = identities
      .map(
        (identity) => `<option value="${identity}" ${identity === activeIdentity ? "selected" : ""}>${identity === "All" ? "All identities" : identity}</option>`
      )
      .join("");
    root.onchange = () => onChange(root.value);
  }

  function renderChartView(league, season) {
    const image = document.querySelector("[data-cluster-image]");
    const chartError = document.querySelector("[data-chart-error]");
    if (!image) return;
    image.src = `assets/tactical_clusters_${league}_${season}.png?v=${Date.now()}`;
    image.alt = `${titleCaseLeague(league)} ${season} tactical map`;
    image.onload = () => chartError?.classList.add("hidden");
    image.onerror = () => chartError?.classList.remove("hidden");
  }

  function renderTeamCards(teams, search, activeIdentity, onOpen) {
    const root = document.querySelector("[data-team-grid]");
    const empty = document.querySelector("[data-empty]");
    if (!root || !empty) return;

    const filtered = Object.entries(teams).filter(([team, info]) => {
      const matchesIdentity = activeIdentity === "All" || info.primary_identity === activeIdentity;
      const matchesSearch = team.toLowerCase().includes(search.toLowerCase());
      return matchesIdentity && matchesSearch;
    });

    if (!filtered.length) {
      root.innerHTML = "";
      empty.classList.remove("hidden");
      return;
    }

    empty.classList.add("hidden");
    root.innerHTML = filtered
      .map(
        ([team, info]) => `
          <article class="team-card">
            <div class="team-card__top">
              <div>
                <div class="team-card__name">${team}</div>
                <div class="team-card__meta">${info.metric} · z ${formatNumber(info.z_score)}</div>
              </div>
              <button class="button-link" data-open-team="${team}">Inspect</button>
            </div>
            <div class="badge-row">
              <span class="badge">${info.primary_identity}</span>
              <span class="badge badge--secondary">${info.secondary_identity}</span>
              ${info.hybrid_flag ? `<span class="badge badge--hybrid">Hybrid</span>` : ""}
            </div>
            <div class="team-card__summary">${info.explanation}</div>
          </article>
        `
      )
      .join("");

    root.querySelectorAll("[data-open-team]").forEach((button) => {
      button.addEventListener("click", () => onOpen(button.dataset.openTeam, teams[button.dataset.openTeam]));
    });
  }

  function openDrawer(team, info) {
    const drawer = document.querySelector("[data-team-drawer]");
    const title = document.querySelector("[data-drawer-title]");
    const subtitle = document.querySelector("[data-drawer-subtitle]");
    const explanation = document.querySelector("[data-drawer-explanation]");
    const scoreRoot = document.querySelector("[data-score-list]");
    const featureRoot = document.querySelector("[data-feature-list]");
    if (!drawer || !title || !subtitle || !explanation || !scoreRoot || !featureRoot) return;

    title.textContent = team;
    subtitle.textContent = `${info.primary_identity} · ${info.secondary_identity} secondary`;
    explanation.textContent = info.assignment_explanation.rationale;

    scoreRoot.innerHTML = Object.entries(info.identity_scores)
      .map(
        ([identity, score]) => `
          <div class="score-bar">
            <div style="display:flex;justify-content:space-between;gap:1rem;">
              <strong>${identity}</strong>
              <span>${formatPercent(score, 1)}</span>
            </div>
            <div class="score-bar__track">
              <div class="score-bar__fill" style="width:${score * 100}%"></div>
            </div>
          </div>
        `
      )
      .join("");

    featureRoot.innerHTML = info.assignment_explanation.top_feature_deltas
      .map(
        (item) => `
          <div class="summary-item">
            <strong>${item.feature_label}</strong>
            <div class="team-card__meta">Team z ${formatNumber(item.team_z_score)} · separation ${formatNumber(item.separation_gain)}</div>
          </div>
        `
      )
      .join("");

    drawer.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    const drawer = document.querySelector("[data-team-drawer]");
    if (!drawer) return;
    drawer.classList.remove("is-open");
    document.body.style.overflow = "";
  }

  async function initExplorerPage() {
    const leagueSelect = document.querySelector("[data-league-select]");
    const seasonSelect = document.querySelector("[data-season-select]");
    const searchInput = document.querySelector("[data-team-search]");
    const identitySelect = document.querySelector("[data-identity-select]");
    const toggleButtons = document.querySelectorAll("[data-view-toggle]");
    const chartView = document.querySelector("[data-chart-view]");
    const tableView = document.querySelector("[data-table-view]");

    if (!leagueSelect || !seasonSelect || !searchInput || !identitySelect || !chartView || !tableView) return;

    let currentTeams = {};
    let currentMetadata = null;
    let activeIdentity = "All";
    let currentSearch = "";

    const applyIdentityFilter = (identity) => {
      activeIdentity = identity;
      renderIdentityFilters(currentTeams, activeIdentity, applyIdentityFilter);
      renderTeamCards(currentTeams, currentSearch, activeIdentity, openDrawer);
    };

    async function refresh() {
      const league = leagueSelect.value;
      const season = seasonSelect.value;
      try {
        const [metadata, teams] = await Promise.all([
          fetchJson(`assets/metadata_${league}_${season}.json`),
          fetchJson(`assets/teams_${league}_${season}.json`),
        ]);
        currentMetadata = metadata;
        currentTeams = teams;
        const availableIdentities = new Set(Object.values(teams).map((item) => item.primary_identity));
        if (activeIdentity !== "All" && !availableIdentities.has(activeIdentity)) {
          activeIdentity = "All";
        }
        renderExplorerMeta(metadata, league, season, teams);
        renderExplorerSummary(metadata, teams);
        renderChartView(league, season);
        renderIdentityFilters(teams, activeIdentity, applyIdentityFilter);
        renderTeamCards(teams, currentSearch, activeIdentity, openDrawer);
        initIcons();
      } catch (error) {
        console.error(error);
        const summaryRoot = document.querySelector("[data-identity-summary]");
        const teamRoot = document.querySelector("[data-team-grid]");
        if (summaryRoot) {
          summaryRoot.innerHTML = `<div class="empty-state">No explorer data is available for this league-season yet.</div>`;
        }
        if (teamRoot) {
          teamRoot.innerHTML = "";
        }
      }
    }

    leagueSelect.value = DEFAULT_LEAGUE;
    seasonSelect.value = DEFAULT_SEASON;
    leagueSelect.addEventListener("change", refresh);
    seasonSelect.addEventListener("change", refresh);
    searchInput.addEventListener("input", () => {
      currentSearch = searchInput.value.trim();
      renderTeamCards(currentTeams, currentSearch, activeIdentity, openDrawer);
    });

    toggleButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const next = button.dataset.viewToggle;
        toggleButtons.forEach((item) => item.classList.toggle("is-active", item === button));
        chartView.classList.toggle("hidden", next !== "chart");
        tableView.classList.toggle("hidden", next !== "table");
      });
    });

    document.querySelectorAll("[data-drawer-close]").forEach((button) => {
      button.addEventListener("click", closeDrawer);
    });

    refresh();
  }

  function init() {
    initIcons();
    initNav();
    initReveal();
  }

  return {
    DEFAULT_LEAGUE,
    DEFAULT_SEASON,
    LEAGUES,
    SEASONS,
    formatPercent,
    formatNumber,
    init,
    initLandingPage,
    initMethodologyPage,
    initExplorerPage,
  };
})();

window.TVMS_SITE = TVMS_SITE;
