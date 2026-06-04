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

  function formatExplorerScoreLabel(value) {
    if (value >= 0.999) {
      return ">99.9%";
    }
    if (value > 0 && value < 0.001) {
      return "<0.1%";
    }
    return formatPercent(value, 1);
  }
  const toDomIdSegment = (value) =>
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "team";
  const getTeamDisclosureIds = (team) => {
    const segment = toDomIdSegment(team);
    return {
      buttonId: `team-toggle-${segment}`,
      panelId: `team-panel-${segment}`,
      titleId: `team-panel-title-${segment}`,
    };
  };

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

  function renderTeamCards(teams, search, activeIdentity, expandedTeam, onToggle, focusTeam = null) {
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
      .map(([team, info]) => {
        const isExpanded = team === expandedTeam;
        const assignment = info.assignment_explanation || {};
        const { buttonId, panelId, titleId } = getTeamDisclosureIds(team);
        const secondaryIdentity = info.secondary_identity || assignment.runner_up_identity || "";
        const secondaryDescription =
          info.secondary_identity_description || assignment.runner_up_description || "No secondary identity description is available.";
        const showHybridContext = Boolean(info.hybrid_flag && secondaryIdentity);
        const marginLabel = showHybridContext
          ? `Hybrid margin ${formatExplorerScoreLabel(info.hybrid_margin ?? assignment.score_gap ?? 0)} between ${info.primary_identity} and ${secondaryIdentity}.`
          : "";
        const identityScores = info.identity_scores || info.scores || {};
        const scoreDistribution = Object.entries(identityScores)
          .sort((left, right) => right[1] - left[1])
          .map(
            ([identity, score]) => `
              <div class="score-bar">
                <div style="display:flex;justify-content:space-between;gap:1rem;">
                  <strong>${identity}</strong>
                  <span>${formatExplorerScoreLabel(score)}</span>
                </div>
                <div class="score-bar__track">
                  <div class="score-bar__fill" style="width:${score * 100}%"></div>
                </div>
              </div>
            `
          )
          .join("");
        const comparisonSummary = showHybridContext
          ? `
              <div class="summary-list team-card__comparison">
                <div class="summary-item">
                  <strong>Secondary identity</strong>
                  <div class="team-card__meta">${secondaryDescription}</div>
                </div>
                <div class="summary-item">
                  <strong>Hybrid margin</strong>
                  <div class="team-card__meta">${marginLabel}</div>
                </div>
              </div>
            `
          : "";
        const topFeatureItems = assignment.top_feature_deltas || [];
        const topFeatures = topFeatureItems
          .map(
            (item) => `
              <div class="summary-item">
                <strong>${item.feature_label}</strong>
                <div class="team-card__meta">Team z ${formatNumber(item.team_z_score)} · separation ${formatNumber(item.separation_gain)}</div>
              </div>
            `
          )
          .join("");

        return `
          <article class="team-card">
            <div class="team-card__top">
              <div>
                <div class="team-card__name">${team}</div>
                <div class="team-card__meta">${info.metric} · z ${formatNumber(info.z_score)}</div>
              </div>
              <button
                id="${buttonId}"
                class="button-link"
                type="button"
                data-toggle-team="${team}"
                aria-expanded="${isExpanded ? "true" : "false"}"
                aria-controls="${panelId}"
                aria-label="${isExpanded ? "Hide" : "Show"} details for ${team}"
              >
                ${isExpanded ? "Hide details" : "Show details"}
              </button>
            </div>
            <div class="badge-row">
              <span class="badge">${info.primary_identity}</span>
              ${showHybridContext ? `<span class="badge badge--secondary">${secondaryIdentity}</span>` : ""}
              ${showHybridContext ? `<span class="badge badge--hybrid">Hybrid</span>` : ""}
            </div>
            <div class="team-card__summary">${info.explanation}</div>
            <div
              id="${panelId}"
              class="card"
              data-team-panel="${team}"
              role="region"
              aria-labelledby="${titleId}"
              ${isExpanded ? "" : "hidden"}
            >
              <h3 id="${titleId}" style="margin-bottom: 0.8rem;">${team} scoring details</h3>
              ${comparisonSummary}
              <div class="card" style="margin-bottom: 1rem;">
                <h3>Identity score distribution</h3>
                ${
                  scoreDistribution
                    ? `<div class="score-list" style="margin-top: 0.8rem;">${scoreDistribution}</div>`
                    : `<div class="team-card__meta" style="margin-top: 0.8rem;">Detailed identity score distribution is only available for 2024+ scored teams.</div>`
                }
              </div>
              <div class="card">
                <h3>Top separating features</h3>
                ${
                  topFeatures
                    ? `<div class="feature-list" style="margin-top: 0.8rem;">${topFeatures}</div>`
                    : `<div class="team-card__meta" style="margin-top: 0.8rem;">Feature-level separation details are only available for 2024+ scored teams.</div>`
                }
              </div>
            </div>
          </article>
        `;
      })
      .join("");

    root.querySelectorAll("[data-toggle-team]").forEach((button) => {
      button.addEventListener("click", () => onToggle(button.dataset.toggleTeam));
    });

    if (focusTeam) {
      const focusTarget = document.getElementById(getTeamDisclosureIds(focusTeam).buttonId);
      focusTarget?.focus({ preventScroll: true });
    }
  }

  async function initExplorerPage() {
    const leagueSelect = document.querySelector("[data-league-select]");
    const seasonSelect = document.querySelector("[data-season-select]");
    const searchInput = document.querySelector("[data-team-search]");
    const identitySelect = document.querySelector("[data-identity-select]");

    if (!leagueSelect || !seasonSelect || !searchInput || !identitySelect) return;

    let currentTeams = {};
    let activeIdentity = "All";
    let currentSearch = "";
    let expandedTeam = null;
    let hasLoadError = false;
    let refreshToken = 0;

    const renderCurrentCards = (focusTeam = null) => {
      if (hasLoadError) {
        const teamRoot = document.querySelector("[data-team-grid]");
        const empty = document.querySelector("[data-empty]");
        if (teamRoot) {
          teamRoot.innerHTML = "";
        }
        empty?.classList.add("hidden");
        return;
      }

      renderTeamCards(currentTeams, currentSearch, activeIdentity, expandedTeam, toggleExpandedTeam, focusTeam);
    };

    const applyIdentityFilter = (identity) => {
      activeIdentity = identity;
      expandedTeam = null;
      renderIdentityFilters(currentTeams, activeIdentity, applyIdentityFilter);
      renderCurrentCards();
    };

    const toggleExpandedTeam = (team) => {
      expandedTeam = expandedTeam === team ? null : team;
      renderCurrentCards(team);
      initIcons();
    };

    async function refresh() {
      const league = leagueSelect.value;
      const season = seasonSelect.value;
      const requestToken = ++refreshToken;
      try {
        const [metadata, teams] = await Promise.all([
          fetchJson(`assets/metadata_${league}_${season}.json`),
          fetchJson(`assets/teams_${league}_${season}.json`),
        ]);
        if (requestToken !== refreshToken) return;
        hasLoadError = false;
        currentTeams = teams;
        expandedTeam = null;
        const availableIdentities = new Set(Object.values(teams).map((item) => item.primary_identity));
        if (activeIdentity !== "All" && !availableIdentities.has(activeIdentity)) {
          activeIdentity = "All";
        }
        renderExplorerMeta(metadata, league, season, teams);
        renderExplorerSummary(metadata, teams);
        renderIdentityFilters(teams, activeIdentity, applyIdentityFilter);
        renderCurrentCards();
        initIcons();
      } catch (error) {
        if (requestToken !== refreshToken) return;
        console.error(error);
        hasLoadError = true;
        currentTeams = {};
        expandedTeam = null;
        activeIdentity = "All";
        const metaRoot = document.querySelector("[data-explorer-summary]");
        const summaryRoot = document.querySelector("[data-identity-summary]");
        const teamRoot = document.querySelector("[data-team-grid]");
        const empty = document.querySelector("[data-empty]");
        if (metaRoot) {
          metaRoot.textContent = `${titleCaseLeague(league)} ${season} data is unavailable right now.`;
        }
        if (summaryRoot) {
          summaryRoot.innerHTML = `<div class="empty-state">No explorer data is available for this league-season yet.</div>`;
        }
        renderIdentityFilters(currentTeams, activeIdentity, applyIdentityFilter);
        if (teamRoot) {
          teamRoot.innerHTML = "";
        }
        empty?.classList.add("hidden");
      }
    }

    leagueSelect.value = DEFAULT_LEAGUE;
    seasonSelect.value = DEFAULT_SEASON;
    leagueSelect.addEventListener("change", refresh);
    seasonSelect.addEventListener("change", refresh);
    searchInput.addEventListener("input", () => {
      currentSearch = searchInput.value.trim();
      renderCurrentCards();
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
    formatExplorerScoreLabel,
    init,
    initLandingPage,
    initMethodologyPage,
    initExplorerPage,
  };
})();

window.TVMS_SITE = TVMS_SITE;
