# TdVisu
![Tests](https://github.com/VaeterchenFrost/tdvisu/workflows/Tests/badge.svg)
![Upload Python Package TEST](https://github.com/VaeterchenFrost/tdvisu/workflows/Upload%20Python%20Package%20TEST/badge.svg)

Visualization for [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) on [tree decompositions](https://en.wikipedia.org/wiki/Tree_decomposition).
Create a graph object for each desired graph that is of interest for the dynamic programming.
Then the visualization generates highlights and adds additional solutions for user-defined time steps.
These snapshots of graphs get written in a supported file-format to a any folder.
For the portable and light weight '.svg' format, all graphs for a timestep can be joined together to provide a thoroughly view on the process of dynamic programming.

With the '.svg' the images are highly customizable, and even combining several timesteps together using svg [animate](https://developer.mozilla.org/en-US/docs/Web/SVG/Element/animate) would be an option.


# Using
[Alubbock:Graphviz](https://anaconda.org/alubbock/graphviz) (or [Graphviz (>=2.38)](https://graphviz.gitlab.io/download/))

[python-benedict](https://pypi.org/project/python-benedict/)

[for dpdb: psycopg2 (2.8.5)](https://www.psycopg.org/docs/index.html)

# How to install

After downloading the latest verion, go to the source-directory. 

With [Conda](https://docs.conda.io/en/latest/) on the system installed, the dependencies for this project can be automatically installed in a new environment - or in a place of your choosing:

Open a *conda-command-prompt* with admin privileges and run the commands from the *gpusat-VISU\tdvisualization_repo* folder:
```shell
conda env create -f .\environment.yml
```
to create a new environment with basic dependencies
```shell
conda activate tdvisu
```
to activate the environment
```shell
dot.exe -c
```
to register the plugins
```shell
pip install --pre .
```
to install the project in the environment (currently in pre-release, to get *pip* see: https://anaconda.org/anaconda/pip)
```shell
python .\tdvisu\visualization.py -h
```
to confirm that the visualization finds all dependencies.
```shell
pip install .[test] 
python -m unittest
```
to run all tests.


# How to use

The visualization needs input in the form of the [Json API](https://github.com/VaeterchenFrost/gpusat-VISU/blob/master/JsonAPI_v1.3.md).
The creation of this file is exemplary implemented in *construct_dpdb_visu.py* or the fork [GPUSAT](https://github.com/VaeterchenFrost/GPUSAT) and *--visufile filename* (optionally disabling preprocessing with *-p*).

Run the python file with the above dependencies installed:
[visualization.py](https://github.com/VaeterchenFrost/gpusat-VISU/blob/master/satvisualization_repo/satvisu/visualization.py)

**visualization.py** takes two parameters, the json-**infile** to read from, and optionally one **outputfolder**.
With both arguments a call from IPython might look like this:

```python
runfile('visualization.py', 
args='visugpusat.json examplefolder')
```

For #SAT it produces for example three different graphs suffixed with a running integer to represent timesteps:

+ *TDStep* the tree decomposition with solved nodes
+ *PrimalGraphStep* the primal graph with currently active variables
+ *IncidenceGraphStep* the bipartite incidence graph with active clauses/variables

Currently the graphs are images encoded in resolution independent **.svg files** (see https://www.lifewire.com/svg-file-4120603)

<img src="Bachelor/images/combined6DA4.svg" alt="Example SharpSat" width="50%"/>
