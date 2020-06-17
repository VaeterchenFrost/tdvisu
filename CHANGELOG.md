# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/ ), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html ).

## [Unreleased]

- JsonAPI.md is now updated with snake_case names and consistent with visualization_data.py 

## [1.1.0] - 2020-06-07
### Added
- Added file utilities.py with several static or shared things like
    - Constants: CFG_EXT, LOGLEVEL_EPILOG, DEFAULT_LOGGING_CFG 
    - Methods: 
        - flatten
        - read_yml_or_cfg combining yaml, json, cfg reader in one
        - logging_cfg configure logging with file or DEFAULT_LOGGING_CFG 
        - helper convert_to_adj from dijkstra.py
        - add_edge_to (edges and adj list)
        - gen_arg infinite Generator
    - Styles:
        - base_style, emphasise_node, style_hide_node, style_hide_edge
    - Graph manipulation:
        - bag_node
        - solution_node
      
- Added file logging.yml (and .ini) with logging configuration for the module [#20]
- Added half the tests for utilities.py

### Changed
- Changed path of image SharpSatExample to the absolute URL for [PyPI].
- Changed names of loggers to absolute name. Should be easy to adjust if needed.
- Changed logging defaults and config in tdvisu/visualization.py and construct_dpdb_visu.py
- Updated ArgumentParser help
- Some fixes of code-style or variable names. 

## [1.0.1] - 2020-06-04
### Added
- Codecoverage with [Codecov]

### Changed
- Changed path of image SharpSatExample to the absolute URL for [PyPI].

## [1.0.0] - 2020-06-04
### Added
- Added svgjoin parameters to JsonAPI [#6]
- Added call to svgjoin from visualization.py
- Added workflow to display the sourcecode-files in [DIRECTORY]

### Changed 
- Moved JsonAPI and conda_packages to /doc
- Updated arguments in svgjoin to be more flexible for multiple joins [#11]
- Fixed scaling mechanism in svgjoin [#13]
- Changed tests from unittest to pytest [#12]

### Removed
- Changelog in JsonAPI.md

## [0.5.1] - 2020-06-01
### Added
- Added publishing Action to [PyPI] [#4]

### Changed
- Changed setup.py with more documentation and simpler functionality.
- Updated Readme with a guide on how to use construct_dpdb_visu [#2]

### Removed
- Removed publishing Action to testpypi [#4]


## [0.5.0-dev1] - 2020-06-01

### Added

- Development version; beginning of the repository [#1]
- Added version.py
- Added module-name to imports
- Added README to tdvisu directly

### Changed
- Fixed usage of `__version__` in tdvisu/construct_dpdb_visu.py

### Removed
- Removed individual versioning 

[#1]: https://github.com/VaeterchenFrost/tdvisu/issues/1
[#2]: https://github.com/VaeterchenFrost/tdvisu/issues/2
[#4]: https://github.com/VaeterchenFrost/tdvisu/issues/4
[#6]: https://github.com/VaeterchenFrost/tdvisu/issues/6
[#11]: https://github.com/VaeterchenFrost/tdvisu/issues/11
[#12]: https://github.com/VaeterchenFrost/tdvisu/issues/12
[#13]: https://github.com/VaeterchenFrost/tdvisu/issues/13
[#20]: https://github.com/VaeterchenFrost/tdvisu/pull/20

[@VaeterchenFrost]: https://github.com/VaeterchenFrost
[PyPI]: https://pypi.org/project/tdvisu/
[mypy]: https://github.com/python/mypy
[DIRECTORY]: https://github.com/VaeterchenFrost/tdvisu/blob/master/DIRECTORY.md
[Codecov]: https://codecov.io/gh/VaeterchenFrost/tdvisu

[Unreleased]: https://github.com/VaeterchenFrost/tdvisu/compare/v1.1.0...master
[1.1.0]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.0
[1.0.1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.0.1
[1.0.0]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.0.0
[0.5.1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v0.5.1
[0.5.0-dev1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v0.5.0-dev1
