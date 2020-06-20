# -*- coding: utf-8 -*-
"""
Helper methods for this module.


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
from configparser import ConfigParser, ParsingError, Error as CfgError
import logging
import logging.config
from itertools import chain
from pathlib import Path
from typing import Generator, Any, Iterable, Iterator, TypeVar, Union, Optional
import yaml

LOGGER = logging.getLogger('utilities.py')

CFG_EXT = ('.ini', '.cfg', '.conf', '.config')
LOGLEVEL_EPILOG = """
Logging levels for python 3.8.2:
    CRITICAL: 50
    ERROR:    40
    WARNING:  30
    INFO:     20
    DEBUG:    10
    NOTSET:    0 (will traverse the logging hierarchy until a value is found)
    """
DEFAULT_LOGGING_CFG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%H:%M:%S'}},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'}},
    'loggers': {
        'visualization.py': {
            'level': 'NOTSET',
            'handlers': ['console'],
            'propagate': False},
        'svgjoin.py': {
            'level': 'NOTSET',
            'handlers': ['console'],
            'propagate': False},
        'reader.py': {
            'level': 'NOTSET',
            'handlers': ['console'],
            'propagate': False},
        'construct_dpdb_visu.py': {
            'level': 'NOTSET',
            'handlers': ['console'],
            'propagate': False}},
    'root': {
        'level': 'WARNING',
        'handlers': ['console']}}

_T = TypeVar('_T')


def flatten(iterable: Iterable[Iterable[_T]]) -> Iterator[_T]:
    """ Flatten at first level.

    Turn ex=[[1,2],[3,4]] into
    [1, 2, 3, 4]
    and [ex,ex] into
    [[1, 2], [3, 4], [1, 2], [3, 4]]
    """
    return chain.from_iterable(iterable)


def read_yml_or_cfg(file: Union[str, Path], prefer_cfg: bool = False,
                    cfg_ext=CFG_EXT) -> Any:
    """
    Read the file and return its content as a python object.

    Parameters
    ----------
    file : file-like
        The file to read from.
    is_cfg : bool, optional
        Indicate that the file should be in 'config' format.
        Assumed only for ext '.ini', '.cfg', '.conf' and '.config'.
        The default is None.

    Returns
    -------
    Any
        Most likely a dict or a ConfigParser supporting get().
        But maybe just a list or a single object.

    """
    err_str = """utilities.read_yml_or_cfg encountered '{}' while
                reading config from '{}' and prefer_cfg={}"""

    file = Path(file)
    if not file.exists():
        raise FileNotFoundError(file.absolute())
    if not file.is_file():
        raise IsADirectoryError(file.resolve())

    # continue with file
    prefer_cfg = prefer_cfg or file.suffix.lower() in cfg_ext
    if prefer_cfg:
        try:
            config = ConfigParser()
            config.read(file)
            if config.sections():
                return config
            print(err_str.format("empty config", file.resolve(), prefer_cfg))
        except (ParsingError, CfgError) as exc:
            print(err_str.format(exc, file.resolve(), prefer_cfg))

    # try yaml file next
    try:
        return yaml.safe_load(file.open())
    except yaml.error.MarkedYAMLError as exc:
        print(err_str.format(exc, file.resolve(), prefer_cfg))
    if not prefer_cfg:
        try:
            config = ConfigParser()
            config.read(file.open())
            return config
        except (ParsingError, CfgError) as exc:
            print(err_str.format(exc, file.resolve(), prefer_cfg))


def logging_cfg(filename: str, prefer_cfg: bool = False,
                loglevel: Optional[int] = None) -> None:
    """Configure logging for this module"""
    LOGGER.info("Read logging configuration from %s", filename)
    read_err = "could not read configuration from '%s'"
    config_err = "could not use logging configuration from '%s'"

    file = Path(filename)
    if prefer_cfg or file.suffix.lower() in CFG_EXT:        # .config
        try:
            logging.config.fileConfig(file, defaults=DEFAULT_LOGGING_CFG)
            if loglevel is not None:
                root = logging.getLogger()
                root.setLevel(loglevel)
                for handler in root.handlers:
                    handler.setLevel(loglevel)
            return
        except OSError:
            LOGGER.warning(read_err, file.resolve())
        except BaseException:   # too general - can we be more specific?
            LOGGER.warning(config_err, file.resolve())
    try:                                                    # dict
        file_content = read_yml_or_cfg(filename, prefer_cfg=prefer_cfg)
        logging.config.dictConfig(file_content)
        if loglevel is not None:
            root = logging.getLogger()
            root.setLevel(loglevel)
            for handler in root.handlers:
                handler.setLevel(loglevel)
        return
    except OSError:
        LOGGER.warning(read_err, file.resolve())
    except BaseException:   # too general - can we be more specific?
        LOGGER.warning(config_err, file.resolve())


def convert_to_adj(edgelist, directed=False) -> dict:
    """
    Helper function to convert the edgelist into the adj-format from NetworkX.

    Parameters
    ----------
    edgelist : array-like of pairs of vertices.
        Simple edgelist. Example:
            [(2, 1), (3, 2), (4, 2), (5, 4)]
    directed : bool, optional
        Whether to add the backward edges too. The default is False.

    Returns
    -------
    adj : dict of edges with empty attributes
        See Docs » Module code » networkx.classes.graph.adj(self)
        for detailed structure.
        Basically: dict of {source1:{target1:{'attr1':value,},},...}
        https://networkx.github.io/documentation/networkx-2.1/_modules/networkx/classes/graph.html
    """
    adj = dict()
    for (source, target) in edgelist:
        if source not in adj:
            adj[source] = {}
        adj[source][target] = {}
        if not directed:
            # add reversed edge
            if target not in adj:
                adj[target] = {}
            adj[target][source] = {}
    return adj


def add_edge_to(edges, adjacency_dict, vertex1, vertex2) -> None:
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


def gen_arg(arg_or_iter: Any) -> Generator:
    """
    Infinite generator for the next argument of `arg_or_iter`.
    If the argument is exhausted, always return the last element.

    Parameters
    ----------
    arg_or_iter : object
        Object to iterate over. Considers three cases:
            string: yields the string as one element indefinitely
            iterable: yields all elements from it, and only the last one after.
            not iterable: yield the object indefinitely
    """
    if isinstance(arg_or_iter, str):
        while True:
            yield arg_or_iter
    elif not isinstance(arg_or_iter, iter_type):
        while True:
            yield arg_or_iter
    else:
        item = None
        for item in arg_or_iter:
            yield item
    while True:
        yield item


def base_style(graph, node, color='white', penwidth='1.0') -> None:
    """Style the node with default fillcolor and penwidth."""
    graph.node(node, fillcolor=color, penwidth=penwidth)


def emphasise_node(graph, node, color='yellow',
                   penwidth='2.5') -> None:
    """Emphasise node with a different fillcolor (default:'yellow')
    and penwidth (default:2.5).
    """
    if color:
        graph.node(node, fillcolor=color)
    if penwidth:
        graph.node(node, penwidth=penwidth)


def style_hide_node(graph, node) -> None:
    """Make the node invisible during drawing."""
    graph.node(node, style='invis')


def style_hide_edge(graph, source, target) -> None:
    """Make the edge source->target invisible during drawing."""
    graph.edge(source, target, style='invis')


def bag_node(head, tail, anchor='anchor', headcolor='white',
             tableborder=0, cellborder=0, cellspacing=0) -> str:
    """HTML format with 'head' as the first label, then appending
    further labels.

    After the 'head' there is an (empty) anchor for edges with a name tag. e.g.
    <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
    <TR><TD BGCOLOR="white">bag 3</TD></TR><TR><TD PORT="anchor"></TD></TR>
    <TR><TD>[1, 2, 5]</TD></TR><TR><TD>03/31/20 09:29:51</TD></TR>
    <TR><TD>dtime=0.0051s</TD></TR></TABLE>
    """
    result = f"""<<TABLE BORDER=\"{tableborder}\" CELLBORDER=\"{cellborder}\"
              CELLSPACING=\"{cellspacing}\">
              <TR><TD BGCOLOR=\"{headcolor}\">{head}</TD></TR>
              <TR><TD PORT=\"{anchor}\"></TD></TR>"""

    if isinstance(tail, str):
        result += f"<TR><TD>{tail}</TD></TR>"
    else:
        for label in tail:
            result += f"<TR><TD>{label}</TD></TR>"

    result += "</TABLE>>"
    return result


def solution_node(
        solution_table,
        toplabel: str = '',
        bottomlabel: str = '',
        transpose: bool = False,
        linesmax: int = 1000,
        columnsmax: int = 50) -> str:
    """Fill the node from the 2D 'solution_table' (columnbased!).
    Optionally add a line above and/or below the table.

    solution_table : 2D-arraylike, entries get converted to str

    toplabel : string, placed above the table

    bottomlabel : string, placed below the table

    transpose : bool, whether to transpose the solution_table before
    processing

    linesmax : int, if positive it indicates the
            maximum number of lines in the table to display.

    columnsmax : int, if positive it indicates the
            maximum number of columns to display + the last.

    Example structure for four columns:
    |----------|
    | toplabel |
    ------------
    |v1|v2|v3|v4|
    |0 |1 |0 |1 |
    |1 |1 |0 |0 |
    ...
    ------------
    | botlabel |
    |----------|
    """
    result = ''
    if toplabel:
        result += toplabel + '|'

    if len(solution_table) == 0:
        result += 'empty'
    else:
        if transpose:
            solution_table = list(zip(*solution_table))

        # limit lines backwards from length of column
        vslice = (min(-1, linesmax - len(solution_table[0]))
                  if linesmax > 0 else -1)
        # limit columns forwards minus one
        hslice = (min(len(solution_table), columnsmax)
                  if columnsmax > 0 else len(solution_table)) - 1

        result += '{'                                       # insert table
        for column in solution_table[:hslice]:
            result += '{'                                   # start column
            for row in column[:vslice]:
                result += str(row) + '|'
            if vslice < -1:     # add one indicator of shortening
                result += '...' + '|'
            for row in column[-1:]:
                result += str(row)
            result += '}|'      # sep. between columns
        # adding one column-skipping indicator
        if hslice < len(solution_table) - 1:
            result += '{'                                   # start column
            for row in column[:vslice]:
                result += '...' + '|'
            if vslice < -1:     # add one indicator of shortening
                result += '...' + '|'
            for row in column[-1:]:
                result += '...'
            result += '}|'      # sep. between columns
        # last column (usually a summary of the previous cols)
        for column in solution_table[-1:]:
            result += '{'                                   # start column
            for row in column[:vslice]:
                result += str(row) + '|'
            if vslice < -1:     # add one indicator of shortening
                result += '...' + '|'
            for row in column[-1:]:
                result += str(row)
            result += '}'      # sep. between columns
        result += '}'                                       # close table

    if bottomlabel:
        result += '|' + bottomlabel

    return '{' + result + '}'
