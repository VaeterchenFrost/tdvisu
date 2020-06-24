# -*- coding: utf-8 -*-
"""
Testing utilities.py

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
from pytest import param, mark, raises
from tdvisu.utilities import flatten, convert_to_adj, add_edge_to


@mark.parametrize(
    "arg",
    [None, 10, 1.4, [1, 2, 3], [None]]
)
def test_cant_flatten(arg):
    """Fail the flatten method with TypeError"""
    with raises(TypeError):
        list(flatten(arg))


@mark.parametrize(
    "arg, expected",
    [((), []),
     ([], []),
     (([None],), [None]),
     ([(1, 2), (3, 4)], [1, 2, 3, 4]),
     ([(1, 2)], [1, 2]),
     ([""], []),
     (["String"], ['S', 't', 'r', 'i', 'n', 'g']),
     (["Str", "Zw", "Dr"], ['S', 't', 'r', 'Z', 'w', 'D', 'r'])
     ]
)
def test_flatten(arg, expected):
    """Test the flatten method."""
    assert list(flatten(arg)) == expected


def test_convert_to_adj():
    """Test the convert_to_adj method"""
    assert convert_to_adj([(2, 1), (3, 2), (4, 2), (5, 4)]) == {
        2: {1: {}, 3: {}, 4: {}}, 1: {2: {}}, 3: {2: {}}, 4: {2: {}, 5: {}}, 5: {4: {}}}


@mark.parametrize(
    "edges, adj, vertex1, vertex2, new_adj",
    [param(set(), {}, 1, 2, {1: {2}, 2: {1}},
           id="empty sets 1"),
     param(set(), {}, "B", "A", {"B": {"A"}, "A": {"B"}},
           id="empty sets 2"),
     param(set([1, 2, 3]), {}, 1, 2, {1: {2}, 2: {1}},
           id="doesnt care about prev elements 1"),
     param(set([None]), {}, "B", "A", {"B": {"A"}, "A": {"B"}},
           id="doesnt care about prev elements 2"),
     param({(1, 2), (2, 3)}, {1: {2}, 2: {1, 3}, 3: {2}}, 3, 1,

           {1: {2, 3}, 2: {1, 3}, 3: {1, 2}},
           id="Closing the triangle"),
     param({('a', 1), (1, 2), (4.3, 2)}, {1: {2, 'a'}, 2: {1, 4.3}, 4.3: {2}, 'a': {1}},
           2, "a",

           {1: {2, 'a'}, 2: {1, 4.3, 'a'}, 4.3: {2}, 'a': {1, 2}},
           id="Even with different elements everything works"),
     ]
)
def test_add_edge_to(edges, adj, vertex1, vertex2, new_adj):
    """Test the add_edge_to method. Sensitive to order in vertices in edges!"""
    expect_edges = set(edges)
    expect_edges.add((vertex1, vertex2))
    add_edge_to(edges, adj, vertex1, vertex2)
    assert edges == expect_edges
    assert adj == new_adj
    # adding second time switched does not change the adjacency
    add_edge_to(edges, adj, vertex2, vertex1)
    assert adj == new_adj
