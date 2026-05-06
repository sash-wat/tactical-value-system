# Project: TVMS (Tactical-Value Mapping System)

This repository contains the Tactical-Value Mapping System, a data-science project focused on North American soccer analysis. It uses advanced metrics to cluster teams by tactical identity and predict player market values.

## Core Mandates

### Architecture & Style
- **Data Source**: Primary data MUST be fetched via the `itscalledsoccer` library from American Soccer Analysis (ASA).
- **Processing Layer**: Use Python (Pandas, Scikit-learn) for all analytical logic.
- **Frontend**: The project landing page is a single-page `index.html` using Tailwind CSS (CDN) and Lucide Icons. Keep it "SaaS-style" with dark mode and mesh gradients.
- **Attribution**: All analytical outputs and the public landing page MUST attribute data to American Soccer Analysis.

### Domain Context
- **Tactical DNA**: This project prioritizes tactical *identity* (e.g., G+ components, PPDA) over final standing or traditional box scores.
- **Value Logic**: "Value" in this system is defined as "System-to-Value Interaction" (how a player's archetype fits a team's cluster).

## Workflow Guidelines
- **Landing Page**: When updating `index.html`, ensure the 'Scroll Reveal' engine (`IntersectionObserver`) remains functional.
- **Documentation**: Design specs live in `docs/specs/` and implementation plans live in `docs/plans/`.
- **Git**: Always push changes to `origin master` to update the GitHub Pages deployment.

## Technical Constraints
- No external CSS files (prefer Tailwind via CDN for the landing page).
- Maintain the "Mesh Gradient" and "Glassmorphism" aesthetic for all UI updates.
