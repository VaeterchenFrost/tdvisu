# -*- coding: utf-8 -*-
"""
Testing visualization.py


Copyright (C) 2020-2024 Martin Röbke

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

import json
from pathlib import Path

import pytest

from tdvisu import visualization as module
from tdvisu.visualization import Visualization, main, read_json

EXPECT_DIR = Path(__file__).parent / 'expected_files'

MINIMAL_JSON = json.dumps({
    "tdTimeline": [[1], [2]],
    "treeDecJson": {
        "bagpre": "bag%s",
        "edgearray": [[1, 2]],
        "labeldict": [
            {"id": 1, "labels": ["a"], "items": [1]},
            {"id": 2, "labels": ["b"], "items": [2]},
        ],
        "num_vars": 1,
    },
})


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


def test_read_json_from_string():
    """Test read_json with a valid JSON string returns the parsed dict."""
    data = '{"key": "value"}'
    result = read_json(data)
    assert result == {"key": "value"}


def test_read_json_from_file(tmp_path):
    """Test read_json with a TextIOWrapper (open file) returns parsed dict."""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"key": "value"}')
    with open(json_file, "r", encoding="UTF-8") as f:
        result = read_json(f)
    assert result == {"key": "value"}


def test_read_json_empty_raises():
    """Test that read_json raises AssertionError for an empty JSON object."""
    with pytest.raises(AssertionError):
        read_json("{}")


def test_read_json_already_parsed():
    """Test read_json with an already-parsed dict uses it directly."""
    data = {"key": "value"}
    result = read_json(data)
    assert result == {"key": "value"}


def test_inspect_json_minimal():
    """Test inspect_json with minimal valid JSON creates VisualizationData."""
    visu = Visualization.__new__(Visualization)
    result = visu.inspect_json(MINIMAL_JSON)
    assert result.incidence_graphs == []
    assert result.general_graphs == []
    assert result.svg_join is None
    assert visu.timeline == [[1], [2]]
    assert visu.bagpre == "bag%s"


def test_inspect_json_missing_key():
    """Test inspect_json raises KeyError when a required key is missing."""
    bad_json = json.dumps({"tdTimeline": [[1]]})
    visu = Visualization.__new__(Visualization)
    with pytest.raises(KeyError):
        visu.inspect_json(bad_json)
