# -*- coding: utf-8 -*-
"""Testing visualization.py

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

import unittest
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


class TestSolutionNode(unittest.TestCase):
    """Testing different solution_node capabilities."""

    def test_solutionnode_empty(self):
        """Solution node with empty args."""
        result = Visualization.solution_node([])
        self.assertEqual(result, "{empty}")

    def test_solutionnode_empty_toplabel(self):
        """Solution node with one toplabel."""
        result = Visualization.solution_node([], "top")
        self.assertEqual(result, "{top|empty}")

    def test_solutionnode_empty_bottomlabel(self):
        """Solution node with one bottomlabel."""
        result = Visualization.solution_node([], bottomlabel="bottom")
        self.assertEqual(result, "{empty|bottom}")

    def test_solutionnode_transpose(self):
        """Solution node with both labels and transposed SOLUTIONTABLE1."""
        result = Visualization.solution_node(
            SOLUTIONTABLE1, "top", "bottom", transpose=True)
        self.assertEqual(
            result, "{top|{{id|v1|v2|v3|nSol}|{0|1|2|4|0}}|bottom}")

    def test_solutionnode_fulltable(self):
        """Solution node with SOLUTIONTABLE1 not transposed."""
        result = Visualization.solution_node(SOLUTIONTABLE1)
        self.assertEqual(result, "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}")

        result = Visualization.solution_node(SOLUTIONTABLE1, "top", "bottom")
        self.assertEqual(
            result, "{top|{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}|bottom}")

    def test_solutionnode_only_header(self):
        """Solution node with only one line."""
        solutionTable = [["id"], ["v1"],
                         ["v2"], ["v3"],
                         ["nSol"]]
        result = Visualization.solution_node(solutionTable)
        self.assertEqual(result, "{{{id}|{v1}|{v2}|{v3}|{nSol}}}")

        result = Visualization.solution_node(solutionTable, "top", "bottom")
        self.assertEqual(result, "{top|{{id}|{v1}|{v2}|{v3}|{nSol}}|bottom}")

    def test_solutionnode_header_numbers(self):
        """Solution node with different number formats."""
        result = Visualization.solution_node(SOLUTIONTABLEINT)
        self.assertEqual(result, "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}")

        result = Visualization.solution_node(SOLUTIONTABLEFLOAT)
        self.assertEqual(
            result, "{{{id|0.1}|{v1|1.0}|{v2|2.2222}|{v3|4.4}|{nSol|0.1}}}")


if __name__ == '__main__':
    unittest.main()
