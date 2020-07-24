# -*- coding: utf-8 -*-
"""
Testing svgjoin.py


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

from collections.abc import Iterable as iter_type
from os import makedirs
from os.path import dirname, join
from random import randint
from typing import Generator

from benedict import benedict

from hypothesis import Verbosity, given, settings
from hypothesis.strategies import (
    booleans, floats, integers, lists, none, recursive, text, tuples)

from pytest import mark, param

from tdvisu.svgjoin import append_svg, f_transform, gen_arg


WRITE = False  # ??? Write Testimages instead of just reading them ???

IMAGE_FOLDER = join('expected_files', 'test_sat_and_join')
DIR = join(dirname(__file__), IMAGE_FOLDER)
FILE1 = join(dirname(__file__), 'IncidenceGraphStep11.svg')
FILE2 = join(dirname(__file__), 'PrimalGraphStep11.svg')

MIN, MAX = 5, 1_000_000
# Should be in between sizes considered for image-dimensions!
BASE = randint(20, 3000)
last_random = None


def randomized(lower: int = MIN, upper: int = MAX):
    """Return randint(lower, upper) with the default values
    considered for image dimensions.
    """
    return randint(lower, upper)


def rand_larger(number):
    """Return a random larger image-size than 'number' and save in last_random."""
    global last_random
    last_random = randomized(lower=number + 1)
    return last_random


def rand_smaller(number):
    """Return a random smaller image-size than 'number' and save in last_random."""
    global last_random
    last_random = randomized(upper=number - 1)
    return last_random


class TestNewHeight:
    """Test the transform method in svgjoin"""

    parameters_default = [
        param({'h_one_': BASE, 'h_two_': BASE},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='Only heights (same)'),
        param({'h_one_': BASE, 'h_two_': 2 * BASE},
              {'vertical_snd': 0.0, 'combine_height': 2 * BASE,
               'scale2': 1}, id='Only heights (larger)'),
        param({'h_one_': BASE, 'h_two_': 0.5 * BASE},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='Only heights (smaller)'),
        param({'h_one_': BASE, 'h_two_': BASE, 'v_bottom': None},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='Default v_bottom'),
        param({'h_one_': BASE, 'h_two_': BASE, 'v_bottom': None, 'v_top': None},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='Default v_bottom&v_top'),
        param({'h_one_': BASE, 'h_two_': BASE, 'scale2': 1},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='Default scale2')]

    parameters_moving = [
        param({'h_one_': BASE, 'h_two_': BASE, 'v_bottom': 1, 'v_top': 0},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id='static'),
        param({'h_one_': BASE, 'h_two_': BASE, 'v_bottom': 0, 'v_top': 1},
              {'vertical_snd': 0.0, 'combine_height': BASE,
               'scale2': 1}, id="switched bottom and top -> "
              "should switch automatically!"),
        param({'h_one_': BASE, 'h_two_': rand_smaller(BASE), 'v_bottom': 1, 'v_top': 0},
              {'vertical_snd': 0.0,
               'combine_height': BASE, 'scale2': BASE / last_random}, id='scale up to BASE'),
        param({'h_one_': BASE, 'h_two_': rand_larger(BASE), 'v_bottom': 1, 'v_top': 0},
              {'vertical_snd': 0.0,
               'combine_height': BASE, 'scale2': BASE / last_random}, id='scale down to BASE'),
    ]

    @mark.parametrize("arguments,expected", parameters_default)
    def test_parameters_default(self, arguments, expected):
        """Test that the default parameters from f_transform work as expected."""
        result = f_transform(**arguments)
        assert result == expected

    @mark.parametrize("arguments,expected", parameters_moving)
    def test_parameters_moving(self, arguments, expected):
        """Test that different parameters for f_transform work as expected."""
        result = f_transform(**arguments)
        assert result == expected


@given(recursive(booleans() | floats() | none() | text() | integers(),
                 lambda children: lists(children,
                                        min_size=1) | tuples(children,
                                                             children),
                 max_leaves=3))
@settings(verbosity=Verbosity.verbose)
def test_gen_arg(arg):
    """Test the generator in svgjoin"""
    gen = gen_arg(arg)
    assert isinstance(gen, Generator)
    size = randint(10, 40)
    if isinstance(arg, str) or not isinstance(arg, iter_type):
        assert [next(gen) for _ in range(size)] == [arg for _ in range(size)]
    else:
        arg = list(arg)  # be subscriptable
        assert ([next(gen) for _ in range(size)] ==
                arg + [arg[-1] for _ in range(size - len(arg))])


@mark.parametrize(
    "otherargs, filename, reverse",
    [param(dict(), 'result_simple_join', False,
           id="Combine two example svg images to a new one"),
     param(dict(), 'result_simple_join', True,
           id="Test the reverse order"),
     param(dict(centerpad=100), 'result_simple_join_padding', True,
           id="Add horizontal padding"),
     param(dict(v_bottom='center', v_top='center'), 'result_centered_join', False,
           id="Center the image"),
     param(dict(v_bottom='center', v_top='center'), 'result_centered_join', True,
           id="Center the image and reversed")
     ]
)
@mark.parametrize(
    "scale2",
    [1, 2, 0.5, 0.2]
)
def test_append_svg_scaled(otherargs, filename, reverse, scale2, write=WRITE):
    """Combine two example svg images - different scalings for second image."""
    filename += f"_scale{int(scale2*10)}to10_{reverse=}.svg"
    with open(FILE1) as file1:
        im_1 = benedict.from_xml(file1.read())
        with open(FILE2) as file2:
            im_2 = benedict.from_xml(file2.read())
            order = (im_2, im_1) if reverse else (im_1, im_2)
            result = append_svg(*order, scale2=scale2, **otherargs)

            result['svg']['@preserveAspectRatio'] = "xMinYMin"
            if write:
                makedirs(DIR, exist_ok=True)
                with open(join(DIR, filename), 'w') as outfile:
                    result.to_xml(output=outfile, pretty=True)
            with open(join(DIR, filename), 'r') as expected:
                assert result == benedict.from_xml(expected.read())


@mark.parametrize(
    "otherargs, filename, reverse",
    [
        param(dict(v_bottom=0, v_top=1), 'result_same_size', False,
              id="Scale second to same size"),
        param(dict(v_bottom=0, v_top=1), 'result_same_size', True,
              id="Scale first to same size"),
        param(dict(v_bottom='bottom', v_top='center'), 'result_lower_half', False,
              id="Move to lower half"),
        param(dict(v_bottom='center', v_top='top'), 'result_upper_half', False,
              id="Move to upper half"),
        param(dict(v_bottom='center', v_top='top'), 'result_upper_half', True,
              id="Move to upper half and reversed"),
        param(dict(v_bottom='top', v_top=-.5), 'result_top_up', False,
              id="Move to top_-0.5"),
        param(dict(v_bottom=0.2, v_top=-.3), 'result_0p2_up', False,
              id="Move to 0.2_-0.3"),
        param(dict(v_bottom='bottom', v_top=1.5), 'result_1p5_down', False,
              id="Move below bottom_1.5"),
    ]
)
@mark.parametrize(
    "padding",
    [0, 50, 200]
)
def test_append_svg_pinned(otherargs, filename, reverse, padding, write=WRITE):
    """Combine two example svg images - scaling with v_bottom and v_top."""
    filename += f"_padding{padding}_{reverse=}.svg"
    with open(FILE1) as file1:
        im_1 = benedict.from_xml(file1.read())
        with open(FILE2) as file2:
            im_2 = benedict.from_xml(file2.read())
            order = (im_2, im_1) if reverse else (im_1, im_2)
            result = append_svg(*order, centerpad=padding, **otherargs)

            result['svg']['@preserveAspectRatio'] = "xMinYMin"
            if write:
                makedirs(DIR, exist_ok=True)
                with open(join(DIR, filename), 'w') as outfile:
                    result.to_xml(output=outfile, pretty=True)
            with open(join(DIR, filename), 'r') as expected:
                assert result == benedict.from_xml(expected.read())
