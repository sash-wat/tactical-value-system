# Spec: North American Tactical-Value Mapping System (TVMS)

**Date**: 2026-05-05  
**Author**: Gemini CLI  
**Status**: APPROVED

## 1. Background & Motivation
The North American soccer market (MLS, USL, NWSL) is historically undervalued and tactically diverse. While advanced metrics like xG and g+ exist, they are rarely analyzed in the context of a team's tactical environment. A player who looks average in a defensive system might be elite in a high-pressing one. This system aims to quantify that "System-to-Value" interaction to identify market inefficiencies.

## 2. Objective
To build a statistically rich system that:
1. Clusters teams into tactical identities using unsupervised learning.
2. Classifies players into archetypes based on their statistical profiles.
3. Quantifies the impact of a team's system on individual player performance.
4. Predicts player "Fair Market Value" using a machine learning engine.

## 3. High-Level Architecture

### Data Layer
- **Source**: American Soccer Analysis (ASA) via `itscalledsoccer`.
- **Entities**: Teams, Players, Games.
- **Metrics**: 
  - Advanced: g+ (all 6 components), xG, xA, xPass, Verticality.
  - Standard: Goals, Assists, Minutes, Possession %, PPDA (Passes Per Defensive Action), Field Tilt.

### Processing Layer (Phase 1 & 2)
- **Clustering Engine**: Scikit-learn (K-Means/Agglomerative) for Team DNA.
- **Archetyping Engine**: PCA (Principal Component Analysis) followed by Clustering for player profiles.
- **Normalization**: Scaling stats by minutes played and league-wide averages to allow cross-league comparison.

### Analysis Layer (Phase 3)
- **Environment Analysis**: Calculating "Delta-Value" (How much a player's g+ deviates from the expected profile of their tactical cluster).

### Valuation Layer (Phase 4)
- **ML Engine**: Supervised learning (Random Forest or XGBoost) to predict valuation.
- **Features**: Age, Archetype, System-Fit, League Level, and Performance Metrics.

## 4. Sub-Projects & Roadmap

### Phase 1: The Tactical Baseline (Teams)
- **Input**: Team-level aggregates for the last 2-3 seasons.
- **Method**: Unsupervised clustering on tactical KPIs (PPDA, g+ Interrupting, g+ Passing, Average Pass Distance).
- **Outcome**: A definitive map of tactical "schools" in North American soccer.

### Phase 2: Player Archetyping (Profiles)
- **Input**: Player-level aggregates (min 500 mins).
- **Method**: Feature reduction (PCA) to find the core traits of players, then clustering into roles (e.g., "The Progressive Carrier," "The Defensive Screen").
- **Outcome**: A similarity index for every player in the dataset.

### Phase 3: System-Value Interaction
- **Input**: Outputs from Phase 1 and 2.
- **Goal**: Identify:
  - **System Specialists**: High g+ in one specific component that matches the team's primary cluster.
  - **Over-performers**: Players whose value is likely inflated by their environment.
  - **Misused Talents**: Players whose individual archetypes clash with their team system.

### Phase 4: ML Valuation Engine
- **Goal**: Train a model on historical transfer/salary data (where available) and performance to predict "Fair Market Value."

## 5. Success Criteria
- **Validation**: Clusters must be soccer-logical (e.g., all high-pressing teams should end up in the same cluster).
- **Output**: A series of high-impact visuals (Radar charts, Scatter plots with marginal distributions, and "Value vs Price" tables).
- **Feel**: Professional-grade analysis suitable for both data-literate fans and pro scouts.

## 6. Constraints & Risks
- **Data Availability**: g+ is available for USLC/MLS, but standard stats like PPDA may need to be derived from game-level data.
- **League Differences**: Normalizing between MLS (Tier 1) and USLC (Tier 2) will require a "League Strength" coefficient in the ML model.
