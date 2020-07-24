# -*- coding: utf-8 -*-
"""
Testing dijkstra.py


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

from hypothesis import Verbosity, given, settings
from hypothesis.strategies import (
    booleans, floats, integers, none, one_of, text)

from pytest import mark, raises

from tdvisu.dijkstra import DijkstraNoPath, bidirectional_dijkstra as find_path


class TestShortestPath:
    """
    Test the functionality of find_path for simple graphs.
    Should find the shortest path on undirected edges if one is availabe,
    raise ValueError if the source or target are not in the edges,
    and raise DijkstraNoPath otherwise.
    """
    edges_low = {2: {1: {}, 3: {}, 4: {}},
                 1: {2: {}},
                 3: {2: {}},
                 4: {2: {}, 5: {}},
                 5: {4: {}}}

    edges_high = {20: {10: {}, 30: {}, 40: {}},
                  10: {20: {}},
                  30: {20: {}},
                  40: {20: {}, 50: {}},
                  50: {40: {}}}

    def test_normal_path(self):
        """Can find a short path."""
        result = find_path(self.edges_low, 1, 4)
        assert result == (2, [1, 2, 4])

    @mark.parametrize(
        "arg",
        [{1: {}}, edges_low]
    )
    def test_length0(self, arg):
        """Staying on one node."""
        result = find_path(arg, 1, 1)
        assert result == (0, [1])

    @given(
        *[one_of(none(), booleans(), floats(), text(), integers())] * 2
    )
    @settings(verbosity=Verbosity.verbose)
    def test_empty_graph(self, source, target):
        """Empty graph should raise Value Error."""
        with raises(ValueError):
            find_path({}, source, target)

    def test_source_not_in_graph(self):
        """Should raise ValueError"""
        with raises(ValueError):
            find_path(self.edges_low, -1, 4)

    def test_target_not_in_graph(self):
        """Should raise ValueError"""
        with raises(ValueError):
            find_path(self.edges_low, 1, -4)

    def test_no_path(self):
        """Should raise ValueError"""
        with raises(DijkstraNoPath):
            find_path({**self.edges_low, **self.edges_high}, 1, 10)

    @given(floats(-10e7, 10e7))
    def test_simple_weight(self, weight):
        """Weight is one constant function"""
        if weight < 0:
            with raises(ValueError):
                find_path(self.edges_low, 1, 4, lambda u, v, data: weight)
        elif weight > 0:
            result = find_path(self.edges_low, 1, 4, lambda u, v, data: weight)
            assert result == (2 * weight, [1, 2, 4])

    @given(floats(-10e7, 10e7))
    def test_individual_weight(self, weight):
        """Weight is attribute in edges"""
        edges = {k: {target: {'weight': weight}for target in d}
                 for k, d in self.edges_low.items()}
        if weight < 0:
            with raises(ValueError):
                find_path(edges, 1, 4)
        elif weight > 0:
            result = find_path(edges, 1, 4)
            assert result == (2 * weight, [1, 2, 4])
