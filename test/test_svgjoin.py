# -*- coding: utf-8 -*-
"""
Testing svgjoin.py
Might want to consider using unittest.TestCase.assertAlmostEqual in some cases.

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

from os.path import dirname, join
from random import randint
from typing import Generator
from collections.abc import Iterable as iter_type
from pytest import param, mark
from benedict import benedict

from tdvisu.svgjoin import f_transform, append_svg, gen_arg


MIN, MAX = 5, 1e6
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


@mark.parametrize(
    "arg",
    [param(None,
           id="Should accept None as argument"),
     param(randint(1, 100),
           id="One integer in generator"),
     param("Hello Test",
           id="Should yield the string itself"),
     param([None, randint(1, 1e4), None],
           id="Should accept None as element in list"),
     param([[1, 2], "String", None, [[[1]]]],
           id="Should only return elements from the first level")
     ]
)
def test_gen_arg(arg):
    """Test the generator in svgjoin"""
    gen = gen_arg(arg)
    assert isinstance(gen, Generator)
    size = randint(10, 40)
    if isinstance(arg, str) or not isinstance(arg, iter_type):
        assert [next(gen) for _ in range(size)] == [arg for _ in range(size)]
    else:
        assert ([next(gen) for _ in range(size)] ==
                arg + [arg[-1] for _ in range(size - len(arg))])


class TestAppendSvg:
    """Test the append_svg method in svgjoin"""

    DIR = dirname(__file__)
    FILE1 = join(DIR, 'IncidenceGraphStep11.svg')
    FILE2 = join(DIR, 'PrimalGraphStep11.svg')

    def test_simple_join(self):
        """Combine two example svg images to a new one - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(im_1, im_2)
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_simple_join.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_simple_join.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())

    def test_simple_join_switched(self):
        """Test the reverse order - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(im_2, im_1)
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_simple_join_switched.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_simple_join_switched.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())

    def test_simple_join_padding(self):
        """Test the horizontal padding - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(im_2, im_1, centerpad=100)
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_simple_join_padding.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_simple_join_padding.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())

    def test_scaleddown_join(self):
        """Scale larger to same size - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(im_2, im_1, v_bottom=0, v_top=1)
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_scaled_join.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_scaled_join.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())

    def test_centered_smaller_join(self):
        """Center the smaller image - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(
                    im_1, im_2, v_bottom='center', v_top='center')
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_centered_join.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_centered_join.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())

    def test_centered_larger_join(self):
        """Center the smaller image - compare to result."""
        with open(self.FILE1) as file1:
            im_1 = benedict.from_xml(file1.read())
            with open(self.FILE2) as file2:
                im_2 = benedict.from_xml(file2.read())
                result = append_svg(
                    im_2, im_1, v_bottom='center', v_top='center')
                result['svg']['@preserveAspectRatio'] = "xMinYMin"
                # to write:
                with open('result_centered_join2.svg', 'w') as file:
                    result.to_xml(output=file, pretty=True)
                with open(join(self.DIR, 'result_centered_join2.svg'), 'r') as expected:
                    assert result == benedict.from_xml(expected.read())
