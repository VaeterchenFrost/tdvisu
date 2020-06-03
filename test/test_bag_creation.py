# -*- coding: utf-8 -*-
"""
Testing creation of bag strings in visualization.py

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


from tdvisu.visualization import Visualization


SOLUTIONTABLE1 = [["id", "0"], ["v1", "1"],
                  ["v2", "2"], ["v3", "4"],
                  ["nSol", "0"]]

SOLUTIONTABLEINT = [["id", 0], ["v1", 1],
                    ["v2", 2], ["v3", 4],
                    ["nSol", 0]]

SOLUTIONTABLEFLOAT = [["id", 0.1], ["v1", 1.],
                      ["v2", 2.2222], ["v3", 4.4],
                      ["nSol", 0.1]]


class TestSolutionNode:
    """Testing different solution_node capabilities."""

    @staticmethod
    def test_solutionnode_empty():
        """Solution node with empty args."""
        result = Visualization.solution_node([])
        assert result == "{empty}"

    @staticmethod
    def test_solutionnode_empty_toplabel():
        """Solution node with one toplabel."""
        result = Visualization.solution_node([], "top")
        assert result == "{top|empty}"

    @staticmethod
    def test_solutionnode_empty_bottomlabel():
        """Solution node with one bottomlabel."""
        result = Visualization.solution_node([], bottomlabel="bottom")
        assert result == "{empty|bottom}"

    @staticmethod
    def test_solutionnode_transpose():
        """Solution node with both labels and transposed SOLUTIONTABLE1."""
        result = Visualization.solution_node(
            SOLUTIONTABLE1, "top", "bottom", transpose=True)
        assert result == "{top|{{id|v1|v2|v3|nSol}|{0|1|2|4|0}}|bottom}"

    @staticmethod
    def test_solutionnode_fulltable():
        """Solution node with SOLUTIONTABLE1 not transposed."""
        result = Visualization.solution_node(SOLUTIONTABLE1)
        assert result == "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}"

        result = Visualization.solution_node(SOLUTIONTABLE1, "top", "bottom")
        assert result == "{top|{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}|bottom}"

    @staticmethod
    def test_solutionnode_only_header():
        """Solution node with only one line."""
        solution_table = [["id"], ["v1"],
                          ["v2"], ["v3"],
                          ["nSol"]]
        result = Visualization.solution_node(solution_table)
        assert result == "{{{id}|{v1}|{v2}|{v3}|{nSol}}}"

        result = Visualization.solution_node(solution_table, "top", "bottom")
        assert result == "{top|{{id}|{v1}|{v2}|{v3}|{nSol}}|bottom}"

    @staticmethod
    def test_solutionnode_header_numbers():
        """Solution node with different number formats."""
        result = Visualization.solution_node(SOLUTIONTABLEINT)
        assert result == "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}"

        result = Visualization.solution_node(SOLUTIONTABLEFLOAT)
        assert result == "{{{id|0.1}|{v1|1.0}|{v2|2.2222}|{v3|4.4}|{nSol|0.1}}}"
