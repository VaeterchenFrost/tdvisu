# TdVisu

![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
[![PyPI license](https://img.shields.io/pypi/l/tdvisu.svg)](https://pypi.python.org/pypi/tdvisu/)
![Tests](https://github.com/VaeterchenFrost/tdvisu/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/VaeterchenFrost/tdvisu/branch/main/graph/badge.svg)](https://codecov.io/gh/VaeterchenFrost/tdvisu)

![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/vaeterchenfrost/tdvisu?include_prereleases)
[![PyPI version fury.io](https://badge.fury.io/py/tdvisu.svg)](https://pypi.python.org/pypi/tdvisu/)
![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/VaeterchenFrost/tdvisu/latest)
[![PyPI status](https://img.shields.io/pypi/status/tdvisu.svg)](https://pypi.python.org/pypi/tdvisu/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/tdvisu.svg)](https://pypi.python.org/pypi/tdvisu/)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/tdvisu)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/VaeterchenFrost/tdvisu)

---

Visualization for [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) on [tree decompositions](https://en.wikipedia.org/wiki/Tree_decomposition).

Create a graph object for each given graph that is of interest for the dynamic programming.

The visualization generates highlights and adds solution-tables for user defined time steps.

These snapshot of the graphs will be written in a graphviz-supported file-format to a folder of your choosing.

For the portable and light weight '.svg' format, all graphs for a timestep can be joined together to provide a thoroughly view on the process of dynamic programming.

With the '.svg' format the images are highly customizable, and even combining several timesteps together using svg [animate](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate) would be an option in the future.

---

# Using

> Note: see also the steps prepared in the CI/CD [.github/workflows/python-app.yml](https://github.com/VaeterchenFrost/tdvisu/actions/workflows/python-app.yml):

[Graphviz (>=2.38)](https://graphviz.gitlab.io/download/). Be aware of changes in default layouts over different major versions of Graphviz. The project currently tests with `graphviz-version: "12.2.1"`.

[python-benedict[xml]](https://pypi.org/project/python-benedict/)

PostgreSQL adapter for Python: [psycopg (3)](https://www.psycopg.org/docs/index.html)

---

# To register the graphviz plugins

https://gitlab.com/graphviz/graphviz/-/issues/1352

```shell
dot.exe -c
```

# To install

In a command prompt with pip (to get _pip_ see: https://pip.pypa.io/en/stable/) installed:
Just run

```shell
pip install -h (for more information on install options)
pip install tdvisu
```

To download the latest version from the default branch:

```shell
git clone --depth 1 --single https://github.com/VaeterchenFrost/tdvisu
```

# To isolate the dependencies

With [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) on the system installed you can isolate the environment, for example

```shell
virtualenv tdvisu_dir -p 3.12
cd tdvisu_dir/bin/
source activate
# Windows: ./tdvisu_dir/Scripts/activate
```

With [Conda](https://docs.conda.io/en/latest/) on the system installed the dependencies for this project can be automatically installed in a new environment:

Go to the projects base directory.

Open a _conda-command-prompt_ with admin privileges and run the commands from the project folder

- to create a new environment with basic dependencies:

```shell
conda env create -f ./environment.yml
```

- to activate the environment:

```shell
conda activate tdvisu
```

# Install from source

To clone the complete repository:

```shell
git clone https://github.com/VaeterchenFrost/tdvisu
```

To download only the latest version from the default branch:

```shell
git clone --depth 1 --single https://github.com/VaeterchenFrost/tdvisu
```

To install the project from the source folder:

```shell
pip install -h (for more information on install options)
pip install .
```

to confirm that the visualization finds all dependencies:

```shell
python ./tdvisu/visualization.py -h
```

to run all tests:

```shell
pip install .[test]
pytest ./test/
```

---

# How to use

The visualization needs input in the form of the [Json API](https://github.com/VaeterchenFrost/gpusat-VISU/blob/main/JsonAPI_v1.3.md).
The creation of this file is exemplary implemented in _construct_dpdb_visu.py_ or the fork [GPUSAT](https://github.com/VaeterchenFrost/GPUSAT) and _--visufile filename_ (optionally disabling preprocessing with _-p_).

Run the python file with the above dependencies installed:
[visualization.py](https://github.com/VaeterchenFrost/gpusat-VISU/blob/main/satvisualization_repo/satvisu/visualization.py)

**visualization.py** takes two parameters, the json-**infile** to read from, and optionally one **outputfolder**.
With both arguments a run might look like this:

```shell
python tdvisu/visualization.py visugpusat.json examplefolder
```

For #SAT it produces for example three different graphs suffixed with a running integer to represent timesteps:

- _TDStep_ the tree decomposition with solved nodes
- _PrimalGraphStep_ the primal graph with currently active variables highlighted
- _IncidenceGraphStep_ the bipartite incidence graph with active clauses/variables highlighted

The graphs are images encoded in resolution independent **.svg files** (see https://www.lifewire.com/svg-file-4120603)

<p align="center"><img src="https://raw.githubusercontent.com/VaeterchenFrost/tdvisu/main/doc/images/combined6DA4.svg?sanitize=true" width="70%"/></p>

## How to use construct_dpdb_visu.py

After installing the project [dp_on_dbs](https://github.com/hmarkus/dp_on_dbs) with the there listed [requirements](https://github.com/hmarkus/dp_on_dbs#requirements), we need to

- edit the [database.ini](https://github.com/VaeterchenFrost/tdvisu/blob/main/tdvisu/database.ini) with our password to [postgresql](https://www.postgresql.org/)
- Solve a problem with `python dpdb.py [GENERAL-OPTIONS] -f <INPUT-FILE> <PROBLEM> [PROBLEM-SPECIFIC-OPTIONS]`
  - for the problem **VertexCover**
    - with flag `--gr-file` to store the htd Input (if the input was in a different format)
  - for the problem **SharpSat**
    - with flag `--store-formula` to store the formula in the database
- Run
  - **Sat** / **SharpSat**: `python construct_dpdb_visu.py [PROBLEMNUMBER]`
  - **VertexCover**: `python construct_dpdb_visu.py [PROBLEMNUMBER] --twfile [TWFILE]`
    with the file in DIMACS tw-format containing the edges of the graph.

# Installation of the psycopg package 

See https://www.psycopg.org/psycopg3/docs/basic/install.html

**Note** Whatever version of `libpq` psycopg is compiled with, it will be possible to connect to PostgreSQL servers of any [supported version](https://www.psycopg.org/docs/install.html#prerequisites): just install the most recent libpq version or the most practical, without trying to match it to the version of the PostgreSQL server you will have to connect to.

---

# New Release

## Version

- Bump `/version.py` according to the changes made
- Change date to the release day, keep format

## Requirements

In case dependencies have changed, or just to update some, check

- _requirements.txt_
- _stable-requirements.txt_ (using `pip freeze`)
- _setup.py_

## Write Changelog.md

- Add tag with link (see bottom for linking examples)
- Add changes, maybe some are already in _Unreleased_
- Update _Unreleased_ with **(No) unreleased changes**

## Review code

- Run tests (pytest)
- Check codestyle (pylint)

## Push

- Push changes to main
- Wait for all automated checks! (All checks have passed...)

## Create Release

- On the GitHub page go to: Release, **[Draft a new release](https://github.com/VaeterchenFrost/tdvisu/releases/new)**
- Enter v'YOUR VERSION NUMBER' as the tag.
- Add a **Release Title** (could be just the version)
- Add some description (like in the CHANGELOG.md)
- Click on **Publish release** on the bottom

## Should automatically release to [PyPI](https://pypi.org/project/tdvisu/)

- For details see: [Upload Python Package](https://github.com/VaeterchenFrost/tdvisu/blob/main/.github/workflows/python-publish.yml)

**Now you are set for the new release :tada:**

---