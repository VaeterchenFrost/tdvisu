# -*- coding: utf-8 -*-
"""
Bidirectional Dijkstra's Algorithm for finding the shortest path between nodes
in a graph.
For more information on the bidirectional agorithm see for example
cs.princeton.edu/courses/archive/spr06/cos423/Handouts/EPP%20shortest%20path%20algorithms.pdf


Copyright (C) 2020 Martin Röbke <martin.roebke@tu-dresden.de>
Modified sourcecode from NetworkX.

Copyright (C) 2004-2020, NetworkX Developers
Aric Hagberg <hagberg@lanl.gov>
Dan Schult <dschult@colgate.edu>
Pieter Swart <swart@lanl.gov>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the NetworkX Developers nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from heapq import heappop, heappush
from itertools import count


def bidirectional_dijkstra(edges, source, target, weight='weight'):
    r"""Dijkstra's algorithm for shortest paths using bidirectional search.

    Parameters
    ----------
    edges : dict of edges
        See Docs » Module code » networkx.classes.graph.adj(self)
        for detailed structure.
        Basically: dict of {source1:{target1:{'attr1':value,},},...}
        networkx.github.io/documentation/networkx-2.1/_modules/networkx/classes/graph.html

    source : node
       Starting node.

    target : node
       Ending node.

    weight : string or function,
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.

       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number.

    Returns
    -------
    length, path : number and list
       length is the distance from source to target.
       path is a list of nodes on a path from source to target.

    Raises
    ------
    ValueError
        If either `source` or `target` is not in edges.

    DijkstraNoPath
        If no path exists between source and target.

    Examples
    --------


    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    In practice  bidirectional Dijkstra is much more than twice as fast as
    ordinary Dijkstra.

    Ordinary Dijkstra expands nodes in a sphere-like manner from the
    source. The radius of this sphere will eventually be the length
    of the shortest path. Bidirectional Dijkstra will expand nodes
    from both the source and the target, making two spheres of half
    this radius. Volume of the first sphere is `\pi*r*r` while the
    others are `2*\pi*r/2*r/2`, making up half the volume.

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    """
    if source not in edges or target not in edges:
        msg = f"Either source {source} or target {target} is not in edges"
        raise ValueError(msg)

    if source == target:
        return (0, [source])

    weight = _weight_function(weight)
    push = heappush
    pop = heappop
    # Init:  [Forward, Backward]
    dists = [{}, {}]   # dictionary of final distances
    paths = [{source: [source]}, {target: [target]}]  # dictionary of paths
    fringe = [[], []]  # heap of (distance, node) for choosing node to expand
    seen = [{source: 0}, {target: 0}]  # dict of distances to seen nodes

    # initialize fringe heap
    push(fringe[0], (0, next(count()), source))
    push(fringe[1], (0, next(count()), target))
    # neighs for extracting correct neighbor information
    neighs = [edges, edges]
    # variables to hold shortest discovered path
    finaldist = float("inf")
    finalpath = []
    direction = 1
    while fringe[0] and fringe[1]:
        # choose direction
        # direction == 0 is forward direction and direction == 1 is back
        direction = 1 - direction
        # extract closest to expand
        (dist, _, v) = pop(fringe[direction])
        if v in dists[direction]:
            # Shortest path to v has already been found
            continue
        # update distance
        dists[direction][v] = dist  # equal to seen[direction][v]
        if v in dists[1 - direction]:
            # if we have scanned v in both directions we are done
            # we have now discovered the shortest path
            return (finaldist, finalpath)

        for w, d in neighs[direction][v].items():
            if direction == 0:  # forward
                vw_length = dists[direction][v] + weight(v, w, d)
            else:  # back, must remember to change v,w->w,v
                vw_length = dists[direction][v] + weight(w, v, d)
            if w in dists[direction]:
                if vw_length < dists[direction][w]:
                    raise ValueError(
                        "Contradictory paths found: negative weights?")
            elif w not in seen[direction] or vw_length < seen[direction][w]:
                # relaxing
                seen[direction][w] = vw_length
                push(fringe[direction], (vw_length, next(count()), w))
                paths[direction][w] = paths[direction][v] + [w]
                if w in seen[0] and w in seen[1]:
                    # see if this path is better than than the already
                    # discovered shortest path
                    totaldist = seen[0][w] + seen[1][w]
                    if finalpath == [] or finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    raise DijkstraNoPath(f"No path between {source} and {target}.")


class DijkstraNoPath(RuntimeError):
    """Raised when there was no path found during Dijkstra algorithm"""


def _weight_function(weight, multigraph: bool = False):
    """Returns a function that returns the weight of an edge.

    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

    Parameters
    ----------
    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.

    multigraph : bool
        Whether the edges represent a multigraph.
        The default is False.

    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the edge joining those nodes. That function returns
        a number representing the weight of an edge.

    If multigraph is true, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.

    """
    if callable(weight):
        return weight
    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if multigraph:
        return lambda u, v, d: min(edge.get(weight, 1) for edge in d.values())
    return lambda u, v, data: data.get(weight, 1)


if __name__ == "__main__":   # pragma: no cover
    # Show one example and print to console
    EDGES = {2: {1: {}, 3: {}, 4: {}},
             1: {2: {}},
             3: {2: {}},
             4: {2: {}, 5: {}},
             5: {4: {}}}
    RESULT = bidirectional_dijkstra(EDGES, 3, 5)
    print(RESULT)
