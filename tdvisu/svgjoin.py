# -*- coding: utf-8 -*-
"""
Load and manipulate svg images. Could also be streamed as string.


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

import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List, Union

from benedict import benedict

from tdvisu.utilities import gen_arg

LOGGER = logging.getLogger('svg_join.py')


# indices
WIDTH = 2
HEIGHT = 3


def test_viewbox(viewbox: List[float]):
    """Should be of form [0, 0, +x, +y]"""
    assert len(viewbox) == 4, "viewbox should have exactly 4 values"
    assert viewbox[:2] == [0., 0.], "[min-x,min-y] should be zero."
    assert viewbox[WIDTH] > 0, "should have positive width"
    assert viewbox[HEIGHT] > 0, "should have positive height"


def append_svg(
        first_dict: dict,
        snd_dict: dict,
        centerpad: float = 0.,
        v_bottom: float = None,
        v_top: float = None,
        scale2: float = 1,
        ndigits: int = 3) -> dict:
    """Modifies the first of two xml-svg dictionary containing a viewbox to
    append the second svg to the right of the first image.

    The second svg should only have ONE group 'g'.
    Scaling keeps the top-left corner in place.


    Parameters
    ----------
    first_dict : dict
        Dictionary with key 'svg' including one or more 'g' elements and a
        '@viewBox' attribute.
    snd_dict : dict
        Dictionary with key 'svg' including one 'g' element and a '@viewBox' attribute.
    centerpad : float, optional
        Additional padding in units between the two images. The default is 0.
    v_bottom : float, optional
        Vertical bottomline for the second image relative to the size of the first.
        Can even be negative or greater than one.
    v_top : float, optional
        Vertical top for the second image relative to the size of the first.
        Can even be negative or greater than one.
        If smaller than v_bottom they get swapped.
    scale2 : float, optional
        Optional scaling.
    ndigits : int, optional
        Rounding results to that many decimal places. The default is 3.

    Returns
    -------
    dict
        The extended result in the first_dict.

    """

    first_svg = first_dict['svg']
    second_svg = snd_dict['svg']

    # The value of the viewBox attribute is a list of four numbers:
    #     min-x, min-y, width and height.
    #     The numbers separated by whitespace and/or a comma,
    #     which specify a rectangle in user space which is mapped to the
    #     bounds of the viewport established for the associated SVG element.
    # See also
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/viewBox

    pattern = re.compile(r'\s*,\s*|\s+')
    viewbox1: List[float] = list(
        map(float, re.split(pattern, first_svg['@viewBox'])))
    viewbox2: List[float] = list(
        map(float, re.split(pattern, second_svg['@viewBox'])))

    test_viewbox(viewbox1)  # viewbox1 validation
    test_viewbox(viewbox2)  # viewbox2 validation

    trafo_result = f_transform(
        viewbox1[HEIGHT], viewbox2[HEIGHT], v_bottom, v_top, scale2)
    vertical_snd = trafo_result['vertical_snd']
    combine_height = trafo_result['combine_height']
    scale2 = trafo_result['scale2']

    LOGGER.info(
        "Transformed with vertical_snd=%s combine_height=%s scale2=%s",
        *(vertical_snd, combine_height, scale2))

    viewbox1[HEIGHT] = round(combine_height - 0.5)
    h_displacement = float(viewbox1[WIDTH]) + centerpad
    viewbox1[WIDTH] = round(max(float(viewbox1[WIDTH]),
                                h_displacement + scale2 * viewbox2[WIDTH]) - 0.5)

    # new viewbox
    first_svg['@viewBox'] = ' '.join(map(str, viewbox1))  # new viewbox
    # update width and height
    first_svg['@width'] = f"{viewbox1[WIDTH]}pt"
    first_svg['@height'] = f"{viewbox1[HEIGHT]}pt"
    # move second image group next to first
    v_transform = round(max(0, vertical_snd), ndigits)
    transform = f"translate({h_displacement} {v_transform}) scale({scale2}) "
    # now scales with scale2
    transform += second_svg['g'].get('@transform', '')
    second_svg['g']['@transform'] = transform

    if vertical_snd < 0:
        # move first image, add after other transform
        transform = first_svg['g'].get('@transform', '')
        transform += f" translate(0 {round(-vertical_snd,ndigits)})"
        first_svg['g']['@transform'] = transform

    # add group to list of 'g'
    if isinstance(first_svg['g'], list):
        first_svg['g'].append(second_svg['g'])
    else:
        first_svg['g'] = [first_svg['g'], second_svg['g']]

    return first_dict


TRANSFORMATION_EXAMPLE = """
(0,-0.5)===========> (1,-0.5)
 |
 |              ==========v_top (-0.2)
 |   =========0 |        |
 |   |       |  |        |
 |   | first |  | second |
 |   |       |  |        |
 |   =========1 |        |
 |              ==========v_bottom (1.2)
 V (0,1.3)
"""


def f_transform(h_one_, h_two_,
                v_bottom: Union[float, str, None] = None,
                v_top: Union[float, str, None] = None,
                scale2: float = 1) -> Dict[str, float]:
    """Calculate vertical position and scaling of second image.

    The input for v_bottom, v_top is in units from\n
    0: top of first image\n
    1: bottom of first image\n

    See also the 'transformation_example'!


    Parameters
    ----------
    h_one_ : float-like
        Height of the first image.
    h_two_ : float-like
        Height of the second image.
    v_bottom : float or str, optional
        Expected position of bottom of second image. The default is None.
    v_top : float or str, optional
        Expected position of bottom of second image. The default is None.
    scale2 : float, optional
        Scale the second image. Only used if NOT BOTH v_bottom or v_top are set.

    Returns
    -------
    dict[str->float]
        'vertical_snd','combine_height','scale2'

    """
    v_displacement = 0.
    # cast to float
    h_one = float(h_one_)
    h_two = float(h_two_)
    LOGGER.debug("Calculating with h_one=%f h_two=%f", h_one, h_two)
    # normalize values
    conversion = {'bottom': 1, 'center': 0.5, 'top': 0, 'inf': 0,
                  -float('inf'): 1, float('inf'): 0}
    v_bottom = conversion.get(v_bottom, v_bottom)
    if isinstance(v_bottom, str):
        raise ValueError(f"Encountered {v_bottom=} not in {conversion=}")
    v_top = conversion.get(v_top, v_top)
    if isinstance(v_top, str):
        raise ValueError(f"Encountered {v_top=} not in {conversion=}")

    size2 = h_two * scale2
    # Get v_bottom and v_top calculated (special case None for not set)
    if v_bottom is None and v_top is None:
        v_top = 0  # set to top of first
        v_bottom = v_top + size2 / h_one
    elif v_bottom is None:
        # now top is already set
        v_bottom = v_top + size2 / h_one
    elif v_top is None:
        v_top = v_bottom - size2 / h_one
    else:
        if v_bottom == v_top:
            # moving the centerline according to value and scaling
            LOGGER.info(
                "The values of 'v_top', 'v_bottom' are both interpreted "
                "as %f - interpreting as centerline!", v_top)
            half = size2 / h_one / 2
            v_top = v_top - half
            v_bottom = v_bottom + half
        if v_bottom < v_top:  # swap
            v_top, v_bottom = v_bottom, v_top
        # resulting in scaling
        scale2 = (v_bottom - v_top) * h_one / h_two
        size2 = h_two * scale2

    if size2 < 10:
        LOGGER.warning("Image got scaled down to small size (%s)!", size2)

    v_displacement = v_top * h_one

    # bottom - top
    combine_height = (max(1, v_bottom) - min(0, v_top)) * h_one

    return {'vertical_snd': v_displacement,
            'combine_height': combine_height,
            'scale2': scale2}


def svg_join(
        base_names: list,
        folder: str = '',
        num_images: int = 1,
        outname: str = 'combined',
        suffix: str = '%d.svg',
        preserve_aspectratio: str = 'xMinYMin',
        padding: Union[int, Iterable[int]] = 0,
        scale2: Union[float, Iterable[float]] = 1,
        v_top: Union[None, float, str, Iterable[Union[None, float, str]]] = None,
        v_bottom: Union[None, float, str, Iterable[Union[None, float, str]]] = None):
    """
    Joines different svg-images from tdvisu placed in 'folder' for every timestep
    in the horizontal order specified in 'in_names'.

    Parameters
    ----------
    in_names : list
        Base names of the images to join.
        The method appends the extra 'name'+'%d'+'.svg' to every name with the
        numbering for '%d' starting from 1.
    folder : str, optional
        The working directory. The default is the current directory.
    num_images : int, optional
        Expected maximum for 1<=i<=num_images. The default is only 1.
    outname : str, optional
        The base name for the combined svg. The default is "combined".
        The same timestep and ending '.svg' gets appended to the base name.
    padding : int, optional
        Additional padding in units between every two images. The default is 0.
    preserve_aspectratio : str, optional
        See https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/preserveAspectRatio.
        or https://css-tricks.com/scale-svg/#article-header-id-1 .
        The default is "xMinYMin".
    suffix : str, optional
        Change the prefix for each file. The default is "%d.svg".
    scale2 : float, optional
        Scale the second image. Only used if either v_bottom or v_top is None.
    v_bottom : float or str, optional
        Expected position of bottom of second image. The default is None.
    v_top : float or str, optional
        Expected position of bottom of second image. The default is None.


    Returns
    -------
    None.

    """
    LOGGER.info("Starting joining: %s", base_names)
    # names empty?
    if not base_names:
        LOGGER.warning("svg_join found no images to combine!")
        return
    # only one?
    if len(base_names) == 1:
        LOGGER.warning("svg_join called with one file - nothing to join!")
        return
    # use path library for normalizing the path
    folder = Path(folder if folder else '')

    resultname = str(folder / outname) + suffix
    names = [str(folder / name) + suffix for name in base_names]

    gen_padding = gen_arg(padding)
    gen_scale2 = gen_arg(scale2)
    gen_v_top = gen_arg(v_top)
    gen_v_bottom = gen_arg(v_bottom)

    for step in range(1, num_images + 1):
        # first - needs at least two images
        with open(names[0] % step) as file:
            im_1 = benedict.from_xml(file.read())
        with open(names[1] % step) as file:
            im_2 = benedict.from_xml(file.read())

        result = append_svg(im_1, im_2, centerpad=next(gen_padding),
                            v_bottom=next(gen_v_bottom),
                            v_top=next(gen_v_top), scale2=next(gen_scale2))

        # rest:
        for name in names[2:]:
            with open(name % step) as file:
                image = benedict.from_xml(file.read())
            result = append_svg(result, image, centerpad=next(gen_padding),
                                v_bottom=next(gen_v_bottom),
                                v_top=next(gen_v_top), scale2=next(gen_scale2))

        result['svg']['@preserveAspectRatio'] = preserve_aspectratio
        with open(resultname % step, 'w') as file:
            result.to_xml(output=file, pretty=True)

        if step < 10:
            LOGGER.debug("Wrote combined: %s", resultname % step)
    LOGGER.info("Finished svg_join")


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG)
    svg_join(['TDStep', 'graph'],
             'Archive/WheelGraph7',
             outname="default_06sc15_rise",
             v_bottom=[1, .85, .7, .55, .4],
             scale2=1.5,
             num_images=5)
