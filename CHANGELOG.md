# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/ ), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html ).

## [Unreleased]
- No unreleased changes yet.

## [1.1.6] - 2020-08-01
### Added
- Added better property based testing with *hypothesis* [#29]
- Added jobs and setups to test on macos and windows [#31]

### Changed
- *do_sort_nodes* now sorts in correct numeric order. [commit cdfcf6](https://github.com/VaeterchenFrost/tdvisu/commit/cdfcf6c332a63f05b499fe133fada4473ad7524c )
- Fixed some import orders

## [1.1.5] - 2020-07-17
### Added
- Added many new tests.
- Hints for not covered code lines.

### Changed
- Simplified code to parse commandline flags while removing duplications in code.
- Entrypoint for modules visualization and construct_dpdb_visu is now in init().
- Some improvements in utilities.solution_node

## [1.1.4] - 2020-07-14
### Added
- Added the possibility to specify and create multiple graph-visualizations in one file [#25]
- Added test case *test_vc_multiple_and_join* in [commit aa31901](https://github.com/VaeterchenFrost/tdvisu/commit/aa319016ac71f9a54023474bf820cb30929c52a8 )
- Added test cases for [construct_dpdb_visu](https://github.com/VaeterchenFrost/tdvisu/blob/master/test/test_construct_dpdb.py )
- Add pytest-mock to tests_require

### Changed
- Simplified and refactored TDVisu.schema.json 
- Schema now includes possibility to specify multiple instances of generalGraph and incidenceGraph 
- Revisited doc/JsonAPI.md to now include all parameters available
- Renamed test folder expected_images to expected_files
- Updated stable-requirements.txt
- Several minor improvements

## [1.1.3] - 2020-07-09
### Added
- Added *TDVisu.schema.json* to validate the Json-API for TDVisu [#24]
- Added 'col' to allowed formats in tw reader (default string in Mathematica)

### Changed
- Fixed error where database configuration was not found in the directory
- Fixed missing double quotation marks in JsonAPI.md
- Moved JsonAPI.md → *doc/JsonAPI.md*

### Removed
- Removed *generalGraph* and *incidenceGraph* from required arguments in API

## [1.1.2] - 2020-06-26
### Added
- Tests for visualization.py using graphviz in the Github Action too
- Tests for reader.py

### Changed
- Fixed typo that prevented joining SVG in visualization
- Fixed cases where logging.yml was not found in the working directory
- Now using pathlib.Path for most file-related operations
- Unified logging configuration in utilities and made it easier to work with [#22]
- Added more type hints and improved existing ones

## [1.1.1] - 2020-06-25
### Added
- Added problem type **Sat** to tdvisu/construct_dpdb_visu.py 
- Added testcases in file test/test_dijkstra.py

### Changed
- JsonAPI.md is now updated with snake_case names and consistent with visualization_data.py 
- Fixed default value for svg-join **v_top** to *None* from *'top'*
- Improved flexibility in several function parameters
- Improved documentation and comments in several places
- Fixed passing parameters to method *setup_tree_dec_graph*

### Removed
- Removed old dependency from  tdvisu/dijkstra.py on utilities

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
[#22]: https://github.com/VaeterchenFrost/tdvisu/issues/22
[#24]: https://github.com/VaeterchenFrost/tdvisu/issues/24
[#25]: https://github.com/VaeterchenFrost/tdvisu/pull/25
[#29]: https://github.com/VaeterchenFrost/tdvisu/issues/29
[#31]: https://github.com/VaeterchenFrost/tdvisu/issues/31

[@VaeterchenFrost]: https://github.com/VaeterchenFrost
[PyPI]: https://pypi.org/project/tdvisu/
[mypy]: https://github.com/python/mypy
[DIRECTORY]: https://github.com/VaeterchenFrost/tdvisu/blob/master/DIRECTORY.md
[Codecov]: https://codecov.io/gh/VaeterchenFrost/tdvisu

[Unreleased]: https://github.com/VaeterchenFrost/tdvisu/compare/v1.1.6...master
[1.1.6]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.6
[1.1.5]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.5
[1.1.4]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.4
[1.1.3]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.3
[1.1.2]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.2
[1.1.1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.1
[1.1.0]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.1.0
[1.0.1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.0.1
[1.0.0]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v1.0.0
[0.5.1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v0.5.1
[0.5.0-dev1]: https://github.com/VaeterchenFrost/tdvisu/releases/tag/v0.5.0-dev1
