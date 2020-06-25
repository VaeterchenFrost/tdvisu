# -*- coding: utf-8 -*-
"""
Testing visualization.py


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

import argparse
from pathlib import Path

from tdvisu.visualization import main


def test_sat_and_join(tmpdir):
    """Complete visualization run with svgjoin."""
    parser = argparse.ArgumentParser()
    parser.add_argument('infile',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help="Input file for the visualization "
                        "must conform with the 'JsonAPI.md'")
    parser.add_argument('outfolder',
                        help="Folder to output the visualization results")
    parser.add_argument('--loglevel', help="set the minimal loglevel for root")

    # get cmd-arguments
    infile = Path(__file__).parent / 'dbjson4andjoin.json'
    outfolder = Path(tmpdir) / 'temp-test_sat_and_join'
    _args = parser.parse_args([str(infile), str(outfolder)])
    # call main()
    main(_args)
    files = [file for file in outfolder.iterdir() if file.is_file()]
    assert len(files
               ) == 42, "total files"
    assert len([file for file in files if file.suffix == '.svg']
               ) == 24, "svg files"
    assert len([file for file in files if file.suffix == '']
               ) == 18, "dot source files"

    testobjects = [file + str(i) for file in
                   ["IncidenceGraphStep", "PrimalGraphStep", "TDStep"]
                   for i in range(1, 7)]

    expected = [Path(__file__).parent / 'expected_images' / file
                for file in testobjects]

    for file in testobjects:
        with open(Path(__file__).parent / 'expected_images' / file) as expected:
            with open(outfolder / file) as result:
                assert result.read() == expected.read(
                ), f"{file} should be the same"
