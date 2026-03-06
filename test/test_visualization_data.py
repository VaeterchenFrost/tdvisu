# -*- coding: utf-8 -*-
"""
Testing visualization_data.py


Copyright (C) 2020-2024 Martin Röbke

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

from tdvisu.visualization_data import (
    GeneralGraphData,
    IncidenceGraphData,
    SvgJoinData,
    VisualizationData,
)


def test_visualization_data_defaults():
    """Test VisualizationData has expected default field values."""
    data = VisualizationData()
    assert data.incidence_graphs is None
    assert data.general_graphs is None
    assert data.svg_join is None
    assert data.td_file == "TDStep"
    assert data.orientation == "BT"
    assert data.linesmax == 100
    assert data.columnsmax == 20
    assert data.bagcolor == "white"
    assert data.fontsize == 20
    assert data.penwidth == 2.2
    assert data.fontcolor == "black"
    assert len(data.colors) == 14
    assert data.emphasis == {
        "firstcolor": "yellow",
        "secondcolor": "green",
        "firststyle": "filled",
        "secondstyle": "dotted,filled",
    }


def test_visualization_data_custom_emphasis():
    """Custom emphasis values override defaults while keeping unspecified keys."""
    data = VisualizationData(emphasis={"firstcolor": "red"})
    assert data.emphasis["firstcolor"] == "red"
    assert data.emphasis["secondcolor"] == "green"
    assert data.emphasis["firststyle"] == "filled"
    assert data.emphasis["secondstyle"] == "dotted,filled"


def test_visualization_data_empty_emphasis():
    """Empty emphasis dict falls back to all defaults."""
    data = VisualizationData(emphasis={})
    assert data.emphasis == {
        "firstcolor": "yellow",
        "secondcolor": "green",
        "firststyle": "filled",
        "secondstyle": "dotted,filled",
    }


def test_incidence_graph_data_defaults():
    """Test IncidenceGraphData has expected default field values."""
    data = IncidenceGraphData(edges=[])
    assert data.subgraph_name_one == "clauses"
    assert data.subgraph_name_two == "variables"
    assert data.var_name_one == ""
    assert data.var_name_two == ""
    assert data.infer_primal is False
    assert data.infer_dual is False
    assert data.primal_file == "PrimalGraphStep"
    assert data.inc_file == "IncidenceGraphStep"
    assert data.dual_file == "DualGraphStep"
    assert data.fontsize == 16
    assert data.penwidth == 2.2
    assert data.second_shape == "diamond"
    assert data.column_distance == 0.5


def test_incidence_graph_data_custom():
    """Test IncidenceGraphData with custom field values."""
    data = IncidenceGraphData(
        edges=[(1, [2, -3])],
        infer_primal=True,
        primal_file="MyPrimal",
        fontsize=12,
    )
    assert data.edges == [(1, [2, -3])]
    assert data.infer_primal is True
    assert data.primal_file == "MyPrimal"
    assert data.fontsize == 12


def test_general_graph_data_extra_nodes_default():
    """GeneralGraphData.extra_nodes defaults to empty list (not None)."""
    data = GeneralGraphData(edges=[(1, 2)])
    assert data.extra_nodes == []


def test_general_graph_data_defaults():
    """Test GeneralGraphData has expected default field values."""
    data = GeneralGraphData(edges=[(1, 2)])
    assert data.graph_name == "graph"
    assert data.file_basename == "graph"
    assert data.var_name == ""
    assert data.do_sort_nodes is False
    assert data.do_adj_nodes is False
    assert data.fontsize == 20
    assert data.first_color == "yellow"
    assert data.first_style == "filled"
    assert data.second_color == "green"
    assert data.second_style == "dotted,filled"
    assert data.third_color == "red"


def test_general_graph_data_custom_extra_nodes():
    """GeneralGraphData preserves explicitly passed extra_nodes."""
    data = GeneralGraphData(edges=[(1, 2)], extra_nodes=[3, 4])
    assert data.extra_nodes == [3, 4]


def test_svg_join_data_defaults():
    """Test SvgJoinData has expected default field values."""
    data = SvgJoinData(base_names=["a", "b"])
    assert data.folder is None
    assert data.outname == "combined"
    assert data.suffix == "%d.svg"
    assert data.preserve_aspectratio == "xMinYMin"
    assert data.num_images == 1
    assert data.padding == 0
    assert data.scale2 == 1.0
    assert data.v_top is None
    assert data.v_bottom is None


def test_svg_join_data_custom():
    """Test SvgJoinData with custom field values."""
    data = SvgJoinData(
        base_names=["TDStep", "graph"],
        folder="output",
        outname="joined",
        num_images=5,
        padding=10,
        scale2=0.5,
    )
    assert data.base_names == ["TDStep", "graph"]
    assert data.folder == "output"
    assert data.outname == "joined"
    assert data.num_images == 5
    assert data.padding == 10
    assert data.scale2 == 0.5
