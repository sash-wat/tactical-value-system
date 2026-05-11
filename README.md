# TVMS | Tactical-Value Mapping System

A machine-learning-driven approach to mapping team tactical identities and identifying market inefficiencies in North American soccer.

## Overview
This project uses ASA (American Soccer Analysis) data to:
- Cluster teams into tactical identities (Phase 1).
- Classify players into archetypes (Phase 2).
- Quantify system-to-value interaction (Phase 3).
- Predict fair market value (Phase 4).

## Documentation
Design specs and implementation plans are located in the `docs/` directory.

## Development
Install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Regenerate tactical map assets:

```bash
python scripts/generate_assets.py --league mls --season 2025
```

## License
MIT
