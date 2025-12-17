# GitHub Copilot Instructions for TdVisu

## Project Overview

TdVisu is a Python-based visualization tool for dynamic programming on tree decompositions. The project creates graph visualizations for the dynamic programming process, generating SVG images that highlight solution tables and progress at different timesteps.

**Primary Language**: Python (3.9+)

**Key Dependencies**:
- Graphviz system binary (>=2.38, tested with 12.2.1) - external dependency
- graphviz Python package (>=0.20) - Python interface to Graphviz
- psycopg[c] (>=3.2.0) for PostgreSQL connectivity
- python-benedict[xml] (>=0.34.0) for JSON/XML handling
- PyYAML (>=6.0) for configuration

## Project Structure

```
tdvisu/
├── tdvisu/              # Main package directory
│   ├── visualization.py      # Core visualization logic
│   ├── reader.py            # Input file readers (JSON API, DIMACS)
│   ├── visualization_data.py # Data structures for visualization
│   ├── svgjoin.py           # SVG combining utilities
│   ├── utilities.py         # Helper functions
│   ├── dijkstra.py          # Graph algorithms
│   ├── construct_dpdb_visu.py # Database integration for dp_on_dbs
│   ├── version.py           # Version information
│   ├── database.ini         # PostgreSQL configuration
│   └── logging.yml          # Logging configuration
├── test/                # Test suite
├── scripts/             # Utility scripts
├── doc/                 # Documentation and examples
└── setup.py            # Package configuration
```

## Coding Conventions

### Python Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Use descriptive variable names
- Add docstrings for all public functions and classes
- Use `pytest` for testing with `pytest-mock` for mocking

### Documentation
- Use Google-style docstrings
- Include parameter types and return values
- Add examples in docstrings for complex functions
- Keep README.md and CHANGELOG.md up to date

### Testing
- Write unit tests for all new functionality
- Use `pytest` as the test framework
- Use `hypothesis` for property-based testing where applicable
- Run tests with: `pytest ./test/`
- Maintain test coverage (tracked via codecov)

### Git Workflow
- Make minimal, focused changes
- Write clear commit messages
- Update CHANGELOG.md for notable changes
- Run tests before committing

## Key Modules

### visualization.py
The main entry point for creating visualizations. Takes JSON input following the JsonAPI specification and generates SVG graphs.

**Key Functions**:
- Processing JSON input data
- Creating graph objects for tree decomposition, primal graph, and incidence graph
- Generating timestep-based visualizations

### reader.py
Handles reading input files in various formats (JSON, DIMACS tw-format, gr-format).

**Key Classes**:
- `TwReader`: Reads tree decomposition files
- `JsonReader`: Parses JSON input following the JsonAPI

### visualization_data.py
Contains data structures and classes for managing visualization state.

**Key Components**:
- Node and edge representations
- Solution table management
- Highlight and styling information

### svgjoin.py
Utilities for combining multiple SVG files into a single composite visualization.

**Features**:
- SVG parsing and manipulation
- Layout management for multiple graphs
- Preserving viewBox and scaling

### construct_dpdb_visu.py
Integration with the dp_on_dbs project for database-driven dynamic programming visualization.

**Requirements**:
- PostgreSQL database connection
- Configured database.ini file
- Problem-specific handling (VertexCover, SharpSat, etc.)

## Input/Output Formats

### JSON API
The primary input format follows a custom JSON API specification (see `doc/JsonAPI.md`). Key elements:
- Graph definitions (nodes, edges)
- Tree decomposition structure
- Timestep information
- Solution tables and highlights

### Output Formats
- SVG files for each graph type at each timestep
- Files named with suffix pattern: `{GraphType}Step{N}.svg`
- Graph types: TDStep, PrimalGraphStep, IncidenceGraphStep

## Database Integration

The project supports PostgreSQL for storing and retrieving dynamic programming results:
- Configure connection in `tdvisu/database.ini`
- Uses psycopg (version 3) for database connectivity
- Required for `construct_dpdb_visu.py` functionality

## Common Tasks

### Running the Visualization
```bash
python tdvisu/visualization.py input.json output_folder
```

### Installing for Development
```bash
pip install -e .[test]
```

### Running Tests
```bash
pytest ./test/
```

### Linting
```bash
pylint tdvisu/ test/
```

## Best Practices for Contributions

1. **Minimal Changes**: Make the smallest possible changes to achieve the goal
2. **Test Coverage**: Add tests for new functionality
3. **Documentation**: Update documentation for API changes
4. **Dependencies**: Avoid adding new dependencies unless absolutely necessary
5. **Python Version**: Support Python 3.9+ (tested on 3.9, 3.10, 3.11, 3.12, 3.13)
6. **Graphviz Compatibility**: Test with Graphviz 12.2.1 for consistency

## Platform Considerations

### PostgreSQL Requirements
Different platforms require different PostgreSQL client library installations:
- **Windows**: PostgreSQL installer or Command Line Tools
- **macOS**: `brew install postgresql@16` or `brew install libpq`
- **Linux (Debian/Ubuntu)**: `apt-get install postgresql-client-16 libpq-dev`
- **Linux (RHEL/CentOS)**: `dnf install postgresql16 postgresql16-devel`
- **Conda**: `conda install postgresql libpq`

## Related Projects

- [dp_on_dbs](https://github.com/hmarkus/dp_on_dbs) - Dynamic programming on databases
- [GPUSAT](https://github.com/VaeterchenFrost/GPUSAT) - GPU-based SAT solver with visualization support

## Visualization Types

### Tree Decomposition (TD)
Shows the tree structure with bags and their contents, highlighting solved nodes at each timestep.

### Primal Graph
Displays the original problem graph with currently active variables highlighted.

### Incidence Graph
Shows the bipartite graph between clauses and variables (for SAT problems).

## File Formats

### DIMACS tw-format
Tree decomposition format with:
- `s td <bags> <treewidth> <vertices>`
- `b <bag_id> <vertex_list>`
- `<bag_id1> <bag_id2>` for edges

### DIMACS gr-format
Graph format for vertex cover problems:
- `p tw <vertices> <edges>`
- `<vertex1> <vertex2>` for edges

## Release Process

When preparing a new release:
1. Update `tdvisu/version.py` with new version and date
2. Update CHANGELOG.md with changes
3. Run full test suite: `pytest ./test/`
4. Check code style: `pylint tdvisu/`
5. Push to main and wait for CI checks
6. Create GitHub release with version tag
7. PyPI publication happens automatically via GitHub Actions

## License

GNU General Public License v3 or later (GPLv3+)
