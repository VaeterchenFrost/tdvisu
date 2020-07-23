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

import random

from hypothesis import Verbosity, example, given, settings
from hypothesis.strategies import (integers, none, one_of)

from pytest import mark, param, raises

from tdvisu.utilities import (add_edge_to, bag_node, convert_to_adj, flatten,
                              read_yml_or_cfg, solution_node)


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


def test_read_yml_or_cfg_not_file(tmp_path):
    """Test cases of reading not existing files"""
    with raises(FileNotFoundError):
        read_yml_or_cfg(tmp_path / 'file_not_exists')
    with raises(IsADirectoryError):
        read_yml_or_cfg(tmp_path)


def test_read_yml_or_cfg_config(tmp_path, capsys):
    """Test edge cases for reading config"""
    with open(tmp_path / 'file', 'w+') as file:
        file.write('')
        file.flush()
        assert read_yml_or_cfg(file.name, True) == dict()
        captured = capsys.readouterr()
        msg = "utilities.read_yml_or_cfg encountered 'empty config' while"
        assert captured.out.startswith(msg)
        # invalid cfg
        file.write('invalid cfg')
        file.flush()
        assert read_yml_or_cfg(file.name, True) == "invalid cfg"
        captured = capsys.readouterr()
        msg = "utilities.read_yml_or_cfg encountered 'File contains no section headers.\nfile:"
        assert captured.out.startswith(msg)
        # yaml error
    with open(tmp_path / 'yaml', 'w+') as file:
        file.write('{invalid yaml')
        file.flush()
        read_yml_or_cfg(file.name)
        captured = capsys.readouterr()
        msg = "utilities.read_yml_or_cfg encountered 'while parsing a flow mapping"
        assert captured.out.startswith(msg)


def test_bag_node():
    """Test edge cases for bag_node"""
    result = bag_node(
        "my_head",
        "my_tail",
        anchor='my_anchor',
        headcolor='orange',
        tableborder=1,
        cellborder=2,
        cellspacing=10)
    assert result == """<<TABLE BORDER="1" CELLBORDER="2"
              CELLSPACING="10">
              <TR><TD BGCOLOR="orange">my_head</TD></TR>
              <TR><TD PORT="my_anchor"></TD></TR><TR><TD>my_tail</TD></TR></TABLE>>"""


@example(columns=1, lines=2, columnsmax=1, linesmax=0)
# "Testing under maximum"
@example(random.randint(1, 2000), random.randint(1, 15), 2000, 15)
# "Testing defaults linesmax = 1000, columnsmax = 50"
@example(random.randint(1001, 1234), random.randint(51, 123), None, None)
# "Testing directly over maximums"
@example(11, 6, 10, 5)
@example(10 - 1, 5 + 1, 10, 5)
@example(10 - 1, 5 + 4, 10, 5)
@example(10 + 1, 5 - 1, 10, 5)
@example(10 + 4, 5 - 1, 10, 5)
# "Testing over maximums"
@example(random.randint(101, 200), random.randint(16, 30), 100, 15)
@given(*[integers(1, 150)] * 2, *[one_of(none(), integers())] * 2)
@settings(verbosity=Verbosity.verbose)
def test_solution_node_filler(columns, lines, columnsmax, linesmax):
    """Test properties of solution_node with column and lines maximum."""
    if columnsmax is not None:
        columnsmax = max(columnsmax, 2)
    if linesmax is not None:
        linesmax = max(linesmax, 2)
    column_based_table = [['%dL%dC' % (line, column)
                           for line in range(lines)]
                          for column in range(columns)]
    optional_args = dict([param for param in
                          zip(['columnsmax', 'linesmax'],
                              [columnsmax, linesmax])
                          if param[1] is not None])
    fill = '...'
    # no labels (default) COLUMN-BASED:
    result = solution_node(column_based_table, **optional_args, fillstr=fill)
    # defaults from function signature
    lmax = (1000 if linesmax is None else linesmax)
    cmax = (50 if columnsmax is None else columnsmax)

    # columns indication
    assert result.count('{') == result.count('}'), "brackets schould close"
    assert (result.count('{') == 2 + min(columns, cmax + 1)
            ), "columns should match the formula"

    # lines indication
    expect_line_dividers = (min(lines, lmax + 2) * min(columns, cmax + 1) - 1)

    assert (result.count('|') == expect_line_dividers
            ), "line-divider count should match the number in the expected grid."

    # labels, COLUMN-BASED:
    result = solution_node(column_based_table, 'a', 'b', **optional_args)
    assert (result.count('|') == expect_line_dividers + 2
            ), "line-divider count should increase by two with labels."

    # TRANSPOSED:
    # no labels (default)
    result = solution_node(column_based_table, transpose=True, **optional_args)
    # columns indication
    assert result.count('{') == result.count('}'), "brackets schould close"
    assert (result.count('{') == 2 + min(lines, cmax + 1)
            ), "columns should match the formula"
    # lines indication
    expect_line_dividers = (min(columns, lmax + 2) *
                            min(lines, cmax + 1) - 1)

    assert (result.count('|') == expect_line_dividers
            ), "line-divider count should match the number in the expected grid."
    # With labels
    result = solution_node(column_based_table, 'a', 'b', True, **optional_args)
    assert (result.count('|') == expect_line_dividers + 2
            ), "line-divider count should increase by two with labels."

    # number of fillers:
    assert result.count(fill) == (bool(lines >= cmax + 1) * min(columns, lmax + 1) +
                                  bool(columns >= lmax + 2) * min(lines, cmax + 1))
