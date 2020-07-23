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

from pathlib import Path

from tdvisu import visualization as module
from tdvisu.visualization import main

EXPECT_DIR = Path(__file__).parent / 'expected_files'


def test_sat_and_join(tmpdir):
    """Complete visualization run with svgjoin."""

    # get cmd-arguments
    infile = Path(__file__).parent / 'dbjson4andjoin.json'
    outfolder = Path(tmpdir) / 'temp-test_sat_and_join'
    args = [str(infile), str(outfolder)]
    # call main()
    main(args)
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

    for file in testobjects:
        with open(EXPECT_DIR / 'test_sat_and_join' / file) as expected:
            with open(outfolder / file) as result:
                assert result.read() == expected.read(
                ), f"{file} should be the same"


def test_vc_multiple_and_join(tmp_path):
    """Complete visualization run with svgjoin for MinVC and sorted graph."""

    # get cmd-arguments
    infile = Path(__file__).parent / 'visualization_wheelgraph_2graphs.json'
    outfolder = tmp_path / 'temp-test_vc_multiple_and_join'
    args = [str(infile), str(outfolder)]
    # call main()
    main(args)
    files = [file for file in outfolder.iterdir() if file.is_file()]
    assert len(files
               ) == 35, "total files"
    assert len([file for file in files if file.suffix == '.svg']
               ) == 20, "svg files"
    assert len([file for file in files if file.suffix == '']
               ) == 15, "dot source files"

    testobjects = [file + str(i) for file in
                   ["TDStep", "graph", "graph_sorted"]
                   for i in range(1, 5)]

    for file in testobjects:
        with open(EXPECT_DIR / 'test_vc_multiple_and_join' / file) as expected:
            with open(outfolder / file) as result:
                assert result.read() == expected.read(
                ), f"{file} should be the same"


def test_init(mocker):
    """Test that main is called correctly if called as __main__."""
    expected = -1000
    main = mocker.patch.object(module, "main", return_value=expected)
    mock_exit = mocker.patch.object(module.sys, 'exit')
    mocker.patch.object(module, "__name__", "__main__")
    module.init()

    main.assert_called_once()
    assert mock_exit.call_args[0][0] == expected
