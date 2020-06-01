# -*- coding: utf-8 -*-
"""
Adapted DIMACS reader from: https://github.com/hmarkus/dp_on_dbs/tree/master/dpdb
DIMACS is an acronym derived from http://dimacs.rutgers.edu/
Discrete Mathematics and Theoretical Computer Science.

Example usage:

import from tdvisu.reader import TwReader

def read_tw_file(tw_file)
    reader = TwReader()
    inp = r.from_filename(tw_file)

def main()
    file = 'gr5.tw'
    graph = read_tw_file(file)
    print(graph.num_vertices)
    print(graph.num_edges)
    print(graph.edges)


Copyright (C) 2020  Patrick Thier https://github.com/Fend0r, TU Wien,
                    Martin Röbke, TU Dresden

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
import sys


logger = logging.getLogger(__name__)


class Reader():
    """Base class for string-readers."""
    @classmethod
    def from_filename(cls, fname):
        with open(fname, "r") as file:
            return cls.from_string(file.read())

    @classmethod
    def from_filewrapper(cls, fwrapper):
        return cls.from_string(fwrapper.read())

    @classmethod
    def from_stream(cls, stream):
        return cls.from_string(stream.read().decode())

    @classmethod
    def from_string(cls, string):
        instance = cls()
        instance.parse(string)
        return instance

    def parse(self, string):
        pass


class DimacsReader(Reader):
    """Reader for the DIMACS graph data format.
    It is a commonly used exchange format for graphs.
    It stores a single undirected graph.
    Plain text or binary format.
    DIMACS is an acronym derived from http://dimacs.rutgers.edu/
    Discrete Mathematics and Theoretical Computer Science.
    """

    def __init__(self):
        self.problem_solution_type = None
        self.format = None
        self._problem_vars = None

    def parse(self, string) -> None:
        lines = string.split("\n")
        body_start = self.preamble(lines)
        self.store_problem_vars()
        self.body(lines[body_start:])

    def store_problem_vars(self):
        pass

    @staticmethod
    def is_comment(line) -> bool:
        return line.startswith("c ") or line == "c"

    def body(self, lines):
        pass

    def preamble(self, lines) -> int:
        """
        Searches for the preamble line in lines and saves:
            problem_solution_type, format, _problem_vars
        Then returns the index of the next line.

        If no preamble is present:
            Exit with error.

        """
        for lineno, line in enumerate(lines):
            if line.startswith("p ") or line.startswith("s "):
                line = line.split()
                self.problem_solution_type = line[0]
                self.format = line[1]
                self._problem_vars = line[2:]
                return lineno + 1

            if not line or self.is_comment(line):
                continue

            warn = "Invalid content in preamble at line %d: %s"
            logger.warning(warn, lineno, line)

        logger.error("No type found in DIMACS file!")
        sys.exit(1)


def _add_edge_to(edges, adjacency_dict, vertex1, vertex2) -> None:
    """
    Adding (undirected) edge from 'vertex1' to 'vertex2'
    to the edges and adjacency-list.

    Parameters
    ----------
    edges : set-like
        Set of tuples of vertices.
    adjacency_dict : dict-like
        Saves adjecent vertices for each vertex.
    vertex1 : any
        First vertex of the new edge.
    vertex2 : any
        Second vertex of the new edge.

    Returns
    -------
    None

    """
    if vertex1 in adjacency_dict:
        adjacency_dict[vertex1].add(vertex2)
    else:
        adjacency_dict[vertex1] = {vertex2}
    if vertex2 in adjacency_dict:
        adjacency_dict[vertex2].add(vertex1)
    else:
        adjacency_dict[vertex2] = {vertex1}
    edges.add((vertex1, vertex2))


class TwReader(DimacsReader):
    """Dimacs Reader for the 'tw' format (saving directed edges).
    Stores edges and adjacency together with
    the number of vertices and number of edges.
    """

    def __init__(self):
        super().__init__()
        self.edges = set()
        self.adjacency_dict = dict()
        self.num_vertices = self.num_edges = None

    def store_problem_vars(self):
        self.num_vertices = int(self._problem_vars[0])
        self.num_edges = int(self._problem_vars[1])

    def body(self, lines) -> None:
        """Store the content from the given lines in the edges and adjacency_dict."""
        if self.format != "tw":
            logger.error("Not a tw file!")
            sys.exit(1)

        for lineno, line in enumerate(lines):
            if not line or self.is_comment(line):
                continue

            line = line.split()
            if len(line) != 2:
                logger.warning(
                    "Expected exactly 2 vertices at line %d, but %d found",
                    lineno,
                    len(line))
            vertex1 = int(line[0])
            vertex2 = int(line[1])

            _add_edge_to(self.edges, self.adjacency_dict, vertex1, vertex2)

        if len(self.edges) != self.num_edges:
            logger.warning(
                "Number of edges mismatch preamble (%d vs %d)", len(
                    self.edges), self.num_edges)
