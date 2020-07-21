# -*- coding: utf-8 -*-
"""
Visualization Data


Copyright (C) 2020  Martin Röbke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.
    If not, see https://www.gnu.org/licenses/gpl-3.0.html

"""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Union


@dataclass
class SvgJoinData:
    """Class for holding different parameters to join the results."""
    base_names: Union[str, Iterable[str]]
    folder: Optional[str] = None
    outname: str = 'combined'
    suffix: str = '%d.svg'
    preserve_aspectratio: str = 'xMinYMin'
    num_images: int = 1
    padding: Union[int, Iterable[int]] = 0
    scale2: Union[float, Iterable[float]] = 1.0
    v_top: Union[None, float, str, Iterable[Union[None, float, str]]] = None
    v_bottom: Union[None, float, str, Iterable[Union[None, float, str]]] = None


@dataclass
class IncidenceGraphData:
    """Class holding different parameters for the incidence graph."""
    edges: list
    subgraph_name_one: str = 'clauses'
    subgraph_name_two: str = 'variables'
    var_name_one: str = ''
    var_name_two: str = ''
    infer_primal: bool = False
    infer_dual: bool = False
    primal_file: str = 'PrimalGraphStep'
    inc_file: str = 'IncidenceGraphStep'
    dual_file: str = 'DualGraphStep'
    fontsize: int = 16
    penwidth: float = 2.2
    second_shape: str = 'diamond'
    column_distance: float = 0.5


@dataclass
class GeneralGraphData:
    """Class holding different parameters for the general graph."""
    edges: list
    extra_nodes: Optional[list] = None
    graph_name: str = 'graph'
    file_basename: str = 'graph'
    var_name: str = ''
    do_sort_nodes: bool = False
    do_adj_nodes: bool = False
    fontsize: int = 20
    first_color: str = 'yellow'
    first_style: str = 'filled'
    second_color: str = 'green'
    second_style: str = 'dotted,filled'
    third_color: str = 'red'

    def __post_init__(self):
        if self.extra_nodes is None:
            self.extra_nodes = list()


@dataclass
class VisualizationData:
    """Class holding different parameters for Visualization."""
    incidence_graphs: Optional[List[IncidenceGraphData]] = None
    general_graphs: Optional[List[GeneralGraphData]] = None
    svg_join: Optional[SvgJoinData] = None
    td_file: str = 'TDStep'
    colors: Optional[list] = None
    orientation: str = 'BT'
    linesmax: int = 100
    columnsmax: int = 20
    bagcolor: str = 'white'
    fontsize: int = 20
    penwidth: float = 2.2
    fontcolor: str = 'black'
    emphasis: Optional[dict] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = [
                '#0073a1',
                '#b14923',
                '#244320',
                '#b1740f',
                '#a682ff',
                '#004066',
                '#0d1321',
                '#da1167',
                '#604909',
                '#0073a1',
                '#b14923',
                '#244320',
                '#b1740f',
                '#a682ff']
        if self.emphasis is None:
            self.emphasis = dict()
        # merge input over defaults:
        self.emphasis = {**{"firstcolor": 'yellow',
                            "secondcolor": 'green',
                            "firststyle": 'filled',
                            "secondstyle": 'dotted,filled'
                            },
                         **self.emphasis}


if __name__ == "__main__":  # pragma: no cover
    # Just Testing:
    incid = [IncidenceGraphData([])]
    gen = [GeneralGraphData([])]
    data = VisualizationData(incidence_graphs=incid, general_graphs=gen)
    print(data)
