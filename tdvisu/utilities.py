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
from itertools import chain
from collections.abc import Iterable as iter_type
from typing import Generator, Any, Iterable, Iterator, TypeVar


_T = TypeVar('_T')

def flatten(iterable: Iterable[Iterable[_T]]) -> Iterator[_T]:
    """ Flatten at first level.

    Turn ex=[[1,2],[3,4]] into
    [1, 2, 3, 4]
    and [ex,ex] into
    [[1, 2], [3, 4], [1, 2], [3, 4]]
    """
    return chain.from_iterable(iterable)


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
        