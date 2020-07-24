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

from pytest import mark, param

from tdvisu.utilities import solution_node


SOLUTIONTABLE1 = [["id", "0"], ["v1", "1"],
                  ["v2", "2"], ["v3", "4"], ["nSol", "0"]]

SOLUTIONTABLEINT = [["id", 0], ["v1", 1], ["v2", 2], ["v3", 4], ["nSol", 0]]

SOLUTIONTABLEFLOAT = [["id", 0.1], ["v1", 1.], ["v2", 2.2222], ["v3", 4.4],
                      ["nSol", 0.1]]

SOLUTIONHEADER = [["id"], ["v1"], ["v2"], ["v3"], ["nSol"]]


parameters_sol = [
    param({'solution_table': tuple()},
          "{empty}", id='with empty args'),
    param({'solution_table': tuple(), 'toplabel': 'top'},
          "{top|empty}", id='with one toplabel'),
    param({'solution_table': tuple(), 'bottomlabel': 'bottom'},
          "{empty|bottom}", id='with one bottomlabel'),
    param({'solution_table': SOLUTIONTABLE1, 'toplabel': 'top',
           'bottomlabel': 'bottom', 'transpose': True},
          "{top|{{id|v1|v2|v3|nSol}|{0|1|2|4|0}}|bottom}",
          id='with both labels and transposed'),
    param({'solution_table': SOLUTIONTABLE1},
          "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}",
          id='not transposed no label'),
    param({'solution_table': SOLUTIONTABLE1, 'toplabel': 'top',
           'bottomlabel': 'bottom'},
          "{top|{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}|bottom}",
          id='not transposed plus labels'),
    param({'solution_table': SOLUTIONHEADER},
          "{{{id}|{v1}|{v2}|{v3}|{nSol}}}",
          id='only header'),
    param({'solution_table': SOLUTIONHEADER, 'toplabel': 'top',
           'bottomlabel': 'bottom'},
          "{top|{{id}|{v1}|{v2}|{v3}|{nSol}}|bottom}",
          id='only header plus labels'),
    param({'solution_table': SOLUTIONTABLEINT},
          "{{{id|0}|{v1|1}|{v2|2}|{v3|4}|{nSol|0}}}",
          id='conversion of ints in table'),
    param({'solution_table': SOLUTIONTABLEFLOAT},
          "{{{id|0.1}|{v1|1.0}|{v2|2.2222}|{v3|4.4}|{nSol|0.1}}}",
          id='conversion of floats'), ]


@mark.parametrize("arguments,expected", parameters_sol)
def test_solutionnode(arguments, expected):
    """Testing different solution_node capabilities."""

    result = solution_node(**arguments)
    assert result == expected
