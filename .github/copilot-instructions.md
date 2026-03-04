# GitHub Copilot Instructions for TdVisu

## Project Overview

TdVisu is a Python (3.9+) visualization tool for dynamic programming on tree decompositions. Generates SVG graphs showing solution tables and progress at different timesteps.

**Key Dependencies**: Graphviz binary (>=2.38), graphviz Python (>=0.20), psycopg[c] (>=3.2.0), python-benedict[xml] (>=0.34.0), PyYAML (>=6.0)

**Structure**:
- `tdvisu/visualization.py` - Core visualization logic
- `tdvisu/reader.py` - Input file readers (JSON API, DIMACS)
- `tdvisu/visualization_data.py` - Data structures
- `tdvisu/svgjoin.py` - SVG combining utilities
- `tdvisu/construct_dpdb_visu.py` - PostgreSQL integration
- `tdvisu/dijkstra.py` - Graph algorithms
- `test/` - Test suite (pytest + hypothesis)

## Coding Conventions

- **Style**: PEP 8, type hints, Google-style docstrings
- **Testing**: pytest with hypothesis for property-based testing
- **Git**: Minimal changes, clear commits, update CHANGELOG.md
- **Python**: Support 3.9+ (tested on 3.9-3.13)

## Key Modules

- **visualization.py**: Main entry point. Processes JSON (JsonAPI spec) → generates SVG graphs (TD, primal, incidence)
- **reader.py**: Parses input files (JSON API, DIMACS tw/gr formats). Classes: `TwReader`, `JsonReader`
- **visualization_data.py**: Data structures for nodes, edges, solution tables, highlights
- **svgjoin.py**: Combines multiple SVGs into composite visualization
- **construct_dpdb_visu.py**: PostgreSQL integration for dp_on_dbs project (requires database.ini)

## I/O Formats

**Input**: JSON API (see `doc/JsonAPI.md`) with graph definitions, tree decomposition, timesteps, solution tables
**Output**: SVG files per graph type per timestep: `{TDStep|PrimalGraphStep|IncidenceGraphStep}{N}.svg`
**DIMACS formats**: tw-format (tree decomposition), gr-format (vertex cover problems)

## Common Tasks

```bash
# Run visualization
python tdvisu/visualization.py input.json output_folder

# Install for development
pip install -e .[test]

# Run tests
pytest ./test/

# Lint code
pylint tdvisu/ test/
```

## Release Process

1. Update `tdvisu/version.py` (version + date)
2. Update CHANGELOG.md
3. Run: `pytest ./test/` and `pylint tdvisu/`
4. Push to main → wait for CI
5. Create GitHub release → auto-publishes to PyPI
