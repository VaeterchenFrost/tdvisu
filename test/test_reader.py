# -*- coding: utf-8 -*-
"""
Testing reader.py


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

from pathlib import Path
from tdvisu.reader import TwReader


def test_reader():
    """Read a file containing graph edges. Check stored edges and adjacency
    as well as the number of vertices and number of edges."""

    twfile = Path(__file__).parent / 'grda16.tw'

    expected_edges = {(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (3, 5),
                      (4, 3), (4, 5), (4, 6), (5, 3), (5, 4), (6, 4),
                      (6, 7), (6, 15), (7, 6), (7, 8), (7, 14), (8, 7),
                      (8, 9), (9, 8), (9, 10), (9, 11), (10, 9),
                      (11, 9), (11, 12), (11, 14), (12, 11), (12, 13),
                      (12, 14), (13, 12), (14, 7), (14, 11), (14, 12),
                      (15, 6), (15, 16), (16, 15)}

    expected_adj = {1: {2}, 2: {1, 3}, 3: {2, 4, 5}, 4: {3, 5, 6},
                    5: {3, 4}, 6: {4, 7, 15}, 7: {6, 8, 14}, 8: {7, 9},
                    9: {8, 10, 11}, 10: {9}, 11: {9, 12, 14}, 12: {11, 13, 14},
                    13: {12}, 14: {7, 11, 12}, 15: {6, 16}, 16: {15}}

    reader = TwReader.from_filename(twfile)

    assert reader.num_vertices == 16
    assert reader.num_edges == 36
    assert reader.edges == expected_edges
    assert reader.adjacency_dict == expected_adj
