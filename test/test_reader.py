# -*- coding: utf-8 -*-
"""
Testing reader.py


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

from pathlib import Path

import pytest

from tdvisu.reader import DimacsReader, Reader, TwReader


def test_reader_valid_input():
    """Create and test the reader on valid input from a file."""
    twfile = Path(__file__).parent / 'grda16.tw'
    # from filename
    reader = TwReader.from_filename(twfile)
    _reader_assertions(reader)
    # from prepared wrapper
    with open(twfile) as wrapper:
        reader = TwReader.from_filewrapper(wrapper)
        _reader_assertions(reader)
    # from (binary) stream
    with open(twfile, "rb") as binary:
        reader = TwReader.from_stream(binary)
        _reader_assertions(reader)
    # from string
    with open(twfile) as file:
        reader = TwReader.from_string(file.read())
        _reader_assertions(reader)


def test_reader_commented_body():
    """Create and test the reader on valid input from a file with comments in the body."""
    twfile = Path(__file__).parent / 'grda16_comments.tw'
    # from filename
    reader = TwReader.from_filename(twfile)
    _reader_assertions(reader)


def test_reader_has_parse():
    """Test existence of (empty) parse() method."""
    reader = Reader()
    reader.parse("Testcase")


def test_dimacsreader_has_store_problem_vars():
    """Test existence of (empty) store_problem_vars() method."""
    reader = DimacsReader()
    reader.store_problem_vars()


def test_dimacsreader_has_body():
    """Test existence of (empty) body() method."""
    reader = DimacsReader()
    reader.body(lines=["", ""])


def test_reader_inval_preamble(caplog):
    """Test message when a unexpected token in the preamble was encountered."""
    twfile = Path(__file__).parent / 'grda16.tw'
    # from string
    with open(twfile) as file:
        content = "invalid preamble\n" + file.read()
        reader = TwReader.from_string(content)
        _reader_assertions(reader)
        assert (
            "reader.py",
            logging.WARN,
            "Invalid content in preamble at line 0: invalid preamble") in caplog.record_tuples


def test_reader_no_type_found(caplog):
    """Test message and exit when no type could be inferred from the file."""
    content = "c no preamble\n"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        TwReader.from_string(content)  # should raise SystemExit
        assert ("reader.py",
                logging.ERROR,
                "No type found in DIMACS file!") in caplog.record_tuples
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


def test_dimacs_wrong_type_found(caplog):
    """Test message and exit when unexpected type was read from the file."""
    content = "p wrong 16 31\n1 2\n2 1\n"
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        TwReader.from_string(content)  # should raise SystemExit
        assert ("reader.py",
                logging.ERROR,
                "Not a tw file!") in caplog.record_tuples
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


def test_dimacs_col_long_line(caplog):
    """Test message when long line was read in the body."""
    colfile = Path(__file__).parent / 'col_with_long_line.col'

    TwReader.from_filename(colfile)  # should raise SystemExit
    assert (
        "reader.py",
        logging.WARN,
        "Expected exactly 2 vertices at line 1, but 3 found") in caplog.record_tuples
    assert (
        "reader.py",
        logging.WARN,
        "Expected exactly 2 vertices at line 1, but 3 found") in caplog.record_tuples


def test_dimacs_fewer_edges(caplog):
    """Test message when the number of edges mismatches the preamble."""
    content = "p tw 3 3\n1 2\n2 3\n"
    reader = TwReader.from_string(content)
    assert (
        "reader.py",
        logging.WARN,
        "Number of edges mismatch preamble (2 vs 3)") in caplog.record_tuples
    assert reader.num_vertices == 3
    assert reader.num_edges == 3
    assert len(reader.edges) == 2


def _reader_assertions(reader: TwReader):
    """Read a file containing graph edges. Check stored edges and adjacency
    as well as the number of vertices and number of edges.
    """

    expected_edges = {(1, 2), (2, 1), (2, 3), (3, 2), (3, 4), (3, 5),
                      (4, 3), (4, 5), (4, 6), (5, 3), (5, 4), (6, 4),
                      (6, 7), (6, 15), (7, 6), (7, 8), (7, 14), (8, 7),
                      (8, 9), (9, 8), (9, 10), (9, 11), (10, 9),
                      (11, 9), (11, 12), (11, 14), (12, 11), (12, 13),
                      (12, 14), (13, 12), (14, 7), (14, 11), (14, 12),
                      (15, 6), (15, 16), (16, 15)}

    expected_adj = {1: {2}, 2: {1, 3}, 3: {2, 4, 5}, 4: {3, 5, 6},
                    5: {3, 4}, 6: {4, 7, 15}, 7: {6, 8, 14}, 8: {7, 9},
                    9: {8, 10, 11}, 10: {9}, 11: {9, 12, 14}, 12: {11, 13, 14},
                    13: {12}, 14: {7, 11, 12}, 15: {6, 16}, 16: {15}}

    assert reader.num_vertices == 16
    assert reader.num_edges == 36
    assert reader.edges == expected_edges
    assert reader.adjacency_dict == expected_adj
