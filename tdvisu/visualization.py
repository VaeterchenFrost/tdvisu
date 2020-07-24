# -*- coding: utf-8 -*-
"""
Visualization for dynamic programming on tree decompositions.

See also the repositories
https://github.com/hmarkus/dp_on_dbs
and
https://github.com/VaeterchenFrost/GPUSAT


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
import io
import itertools
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List, NewType, Optional, Union

from graphviz import Digraph, Graph

from tdvisu.svgjoin import svg_join
from tdvisu.utilities import (bag_node, base_style, emphasise_node, flatten,
                              get_parser, logging_cfg, solution_node,
                              style_hide_edge, style_hide_node)
from tdvisu.visualization_data import (GeneralGraphData, IncidenceGraphData,
                                       SvgJoinData, VisualizationData)

LOGGER = logging.getLogger('visualization.py')

StrOrIo = NewType('StrOrIo', Union[str, io.TextIOWrapper])


def read_json(json_data: StrOrIo) -> dict:
    """
    Read json data into a callable object.
    Throws AssertionError if the parsed object has length 0.

    Parameters
    ----------
    json_data : String or io.TextIOWrapper
        The object to be read from.

    Returns
    -------
    result : JSON
        The parsed json.

    """
    if isinstance(json_data, str):
        result = json.loads(json_data)
    elif isinstance(json_data, io.TextIOWrapper):
        result = json.load(json_data)
    else:
        LOGGER.warning("read_json called on %s", type(json_data))
        result = json_data
    assert len(result) > 0, "Please input a valid JSON resource!"
    return result


class Visualization:
    """Holds and processes the information needed to provide dot-format
    and image output for the visualization
    of dynamic programming on tree decomposition.
    """

    def __init__(self, infile: StrOrIo, outfolder: Path):
        """Copy needed fields from arguments and create VisualizationData."""
        self.data: VisualizationData = self.inspect_json(infile)
        self.outfolder = Path(outfolder).resolve()
        self.tree_dec_digraph = None
        LOGGER.debug("Initialized: %s", self)

    def inspect_json(self, infile: StrOrIo) -> VisualizationData:
        """Read and preprocess the needed data from the infile into VisualizationData."""
        LOGGER.debug("Reading from: %s", infile)
        visudata = read_json(infile)
        LOGGER.debug("Found keys: %s", visudata.keys())

        try:
            _incid = visudata.get('incidenceGraph', None)
            _general_graph = visudata.get('generalGraph', None)
            _svg_join = visudata.get('svgjoin', None)

            incid_data: List[IncidenceGraphData] = list()
            if _incid:
                if not isinstance(_incid, list):
                    _incid = [_incid]
                # unwrap as list:
                for data in _incid:
                    # add object to incid_data
                    data['edges'] = [[x['id'], x['list']]
                                     for x in data['edges']]
                    incid_data += [IncidenceGraphData(**data)]
            visudata.pop('incidenceGraph', None)

            general_graph_data: List[GeneralGraphData] = list()
            if _general_graph:
                if not isinstance(_general_graph, list):
                    _general_graph = [_general_graph]
                for data in _general_graph:
                    general_graph_data += [GeneralGraphData(**data)]
            visudata.pop('generalGraph', None)

            svg_join_data: Optional[SvgJoinData] = None
            if _svg_join:
                svg_join_data = SvgJoinData(**_svg_join)
            if 'svgjoin' in visudata:
                visudata.pop('svgjoin')

            self.timeline = visudata['tdTimeline']
            visudata.pop('tdTimeline')
            self.tree_dec = visudata['treeDecJson']
            self.bagpre = self.tree_dec['bagpre']
            self.joinpre = self.tree_dec.get('joinpre', 'Join %d~%d')
            self.solpre = self.tree_dec.get('solpre', 'sol%d')
            self.soljoinpre = self.tree_dec.get('soljoinpre', 'solJoin%d~%d')
            visudata.pop('treeDecJson')
        except KeyError as err:
            raise KeyError(f"Key {err} not found in the input Json.")
        return VisualizationData(incidence_graphs=incid_data,
                                 general_graphs=general_graph_data,
                                 svg_join=svg_join_data,
                                 **visudata)

    def setup_tree_dec_graph(
            self,
            rankdir: str = 'BT',
            shape: str = 'box',
            fillcolor: str = 'white',
            style: str = 'rounded,filled',
            margin: str = '0.11,0.01') -> None:
        """Create self.tree_dec_digraph
        strict means not a multigraph - equal edges get merged.

        rankdir sets the direction in which the nodes are built up.
            - normally Bottom-Top or Top-Bottom.
        """
        self.tree_dec_digraph = Digraph(
            'Tree-Decomposition', strict=True,
            graph_attr={'rankdir': rankdir},
            node_attr={
                'shape': shape,
                'fillcolor': fillcolor,
                'style': style,
                'margin': margin})

    def basic_tdg(self) -> None:
        """Create basic bag structure in tree_dec_digraph."""
        for item in self.tree_dec['labeldict']:
            bagname = self.bagpre % str(item['id'])
            self.tree_dec_digraph.node(bagname,
                                       bag_node(bagname, item['labels']))

        self.tree_dec_digraph.edges([(self.bagpre % str(first), self.bagpre % str(
            second)) for (first, second) in self.tree_dec['edgearray']])

    def forward_iterate_tdg(
            self,
            joinpre: str,
            solpre: str,
            soljoinpre: str) -> None:
        """Create the final positions of all nodes with solutions."""
        tdg = self.tree_dec_digraph                 # shorten name

        for i, node in enumerate(self.timeline):    # Create the positions
            if len(node) > 1:
                # solution to be displayed
                id_inv_bags = node[0]
                if isinstance(id_inv_bags, int):
                    last_sol = solpre % id_inv_bags
                    tdg.node(last_sol, solution_node(
                        *(node[1])), shape='record')

                    tdg.edge(self.bagpre % id_inv_bags, last_sol)

                else:                               # joined node with 2 bags
                    suc = self.timeline[i + 1][0]   # get the joined bags

                    LOGGER.debug('joining %s to %s ', node[0], suc)

                    id_inv_bags = tuple(id_inv_bags)
                    last_sol = soljoinpre % id_inv_bags
                    tdg.node(last_sol, solution_node(
                        *(node[1])), shape='record')

                    tdg.edge(joinpre % id_inv_bags, last_sol)
                    # edges
                    for child in id_inv_bags:  # basically "remove" current
                        # TODO check where 2 args are possibly occuring
                        tdg.edge(
                            self.bagpre % child
                            if isinstance(child, int) else joinpre % child,
                            self.bagpre % suc
                            if isinstance(suc, int) else joinpre % suc,
                            style='invis',
                            constraint='false')
                        tdg.edge(self.bagpre % child if isinstance(child, int)
                                 else joinpre % child,
                                 joinpre % id_inv_bags)
                    tdg.edge(joinpre % id_inv_bags, self.bagpre % suc
                             if isinstance(suc, int) else joinpre % suc)

    def backwards_iterate_tdg(self, joinpre: str, solpre: str, soljoinpre: str,
                              view: bool = False) -> None:
        """Cut the single steps back and update emphasis acordingly."""
        tdg = self.tree_dec_digraph     # shorten name
        last_sol = ""
        _filename = self.outfolder / self.data.td_file
        for i, node in enumerate(reversed(self.timeline)):
            id_inv_bags = node[0]
            LOGGER.debug("%s: Reverse traversing on %s", i, id_inv_bags)

            if i > 0:
                # Delete previous emphasis
                prevhead = self.timeline[len(self.timeline) - i][0]
                bag = (
                    self.bagpre %
                    prevhead if isinstance(
                        prevhead,
                        int) else joinpre %
                    tuple(prevhead))
                base_style(tdg, bag)
                if last_sol:
                    style_hide_node(tdg, last_sol)
                    style_hide_edge(tdg, bag, last_sol)
                    last_sol = ""

            if len(node) > 1:
                # solution to be displayed
                if isinstance(id_inv_bags, int):
                    last_sol = solpre % id_inv_bags
                    emphasise_node(tdg, last_sol)
                    tdg.edge(self.bagpre % id_inv_bags, last_sol)
                else:  # joined node with 2 bags
                    id_inv_bags = tuple(id_inv_bags)
                    last_sol = soljoinpre % id_inv_bags
                    emphasise_node(tdg, last_sol)

            emphasise_node(tdg,
                           self.bagpre %
                           id_inv_bags if isinstance(
                               id_inv_bags,
                               int) else joinpre %
                           id_inv_bags)

            tdg.render(
                view=view, format='svg',
                filename=str(_filename) + str(len(self.timeline) - i)
            )

    def tree_dec_timeline(self, view: bool = False) -> None:
        """Main-method for handling all construction of the timeline."""

        self.setup_tree_dec_graph(
            rankdir=self.data.orientation,
            fillcolor=self.data.bagcolor)
        self.basic_tdg()

        # Iterate labeldict
        self.forward_iterate_tdg(
            joinpre=self.joinpre,
            solpre=self.solpre,
            soljoinpre=self.soljoinpre)
        self.backwards_iterate_tdg(
            view=view,
            joinpre=self.joinpre,
            solpre=self.solpre,
            soljoinpre=self.soljoinpre)

        # Prepare supporting graph timeline

        _timeline: List[Optional[List[int]]] = []
        for step in self.timeline:
            if len(step) < 2:
                _timeline.append(None)
            elif isinstance(step[0], int):
                _timeline.append(
                    next(
                        (item.get('items') for item in self.tree_dec['labeldict']
                         if item['id'] == step[0])))
            else:
                # Join operation - no clauses involved in computation
                _timeline.append(None)

        if self.data.incidence_graphs:
            for incidence_data in self.data.incidence_graphs:
                self.prepare_incidence(incidence_data, _timeline, view)
                LOGGER.info("Created incidence-graph for file='%s'",
                            incidence_data.inc_file)
        if self.data.general_graphs:
            for graph_data in self.data.general_graphs:
                self.general_graph(timeline=_timeline, view=view,
                                   **asdict(graph_data))
                LOGGER.info(
                    "Created general-graph for file='%s'",
                    graph_data.file_basename)
        if self.data.svg_join:
            self.call_svgjoin()

    def prepare_incidence(self, incid, _timeline, view):
        """Prepare incidence construction."""
        if incid.infer_primal or incid.infer_dual:
            # prepare incid edges with abs:
            abs_clauses = [[cl[0], list(map(abs, cl[1]))]
                           for cl in incid.edges]
        if incid.infer_primal:
            # vertex for each variable + edge if the variables
            # occur in the same clause:
            primal_edges = set(flatten(             # remove duplicates
                [itertools.combinations(cl[1], 2)
                 for cl in abs_clauses]))
            # check if any node is really isolated:
            isolated = [cl[1][0] for cl in abs_clauses
                        if len(cl[1]) == 1 and
                        not any(cl[1][0] in sl for sl in primal_edges)]

            self.general_graph(
                timeline=_timeline,
                edges=primal_edges,
                extra_nodes=set(isolated),
                graph_name=incid.primal_file,
                file_basename=incid.primal_file,
                var_name=incid.var_name_two)
            LOGGER.info("Created infered primal-graph")

        if incid.infer_dual:
            # Edge, if clauses share the same variable
            dual_edges = [(cl[0], other[0])
                          for i, cl in enumerate(abs_clauses)
                          for other in abs_clauses[i + 1:]  # no multiples
                          if any(var in cl[1] for var in other[1])]
            # check if any clause is isolated:
            isolated = [cl[0] for cl in abs_clauses
                        if not any(cl[0] in sl for sl in dual_edges)]

            self.general_graph(
                timeline=_timeline,
                edges=dual_edges,
                extra_nodes=set(isolated),
                graph_name=incid.dual_file,
                file_basename=incid.dual_file,
                var_name=incid.var_name_one)
            LOGGER.info("Created infered dual-graph")

        self.incidence(
            edges=incid.edges,
            timeline=_timeline,
            inc_file=incid.inc_file,
            num_vars=self.tree_dec['num_vars'],
            colors=self.data.colors, view=view,
            fontsize=incid.fontsize,
            penwidth=incid.penwidth,
            basefill=self.data.bagcolor,
            var_name_one=incid.var_name_one,
            var_name_two=incid.var_name_two,
            column_distance=incid.column_distance)

    def general_graph(
            self,
            timeline: Iterable[Optional[List[int]]],
            edges: Iterable[Iterable[int]],
            extra_nodes: Iterable[int] = tuple(),
            view: bool = False,
            fontsize: int = 20,
            fontcolor: str = 'black',
            penwidth: float = 2.2,
            first_color: str = 'yellow',
            first_style: str = 'filled',
            second_color: str = 'green',
            second_style: str = 'dotted,filled',
            third_color: str = 'red',
            graph_name: str = 'graph',
            file_basename: str = 'graph',
            do_sort_nodes: bool = True,
            do_adj_nodes: bool = True,
            var_name: str = '') -> None:
        """
        Creates one graph emphasized for the given timeline.

        Parameters
        ----------
        edges : Iterable of: {int, int}
            All edges between nodes in the graph.
            Should NOT contain self-edges!
            BOTH edges (x, y) and (y, x) could be in the edgelist.

        extra_nodes : Iterable of int
            Nodes that are probably not in the edges, but should be rendered.

        TIMELINE : Iterable of: None | [int...]
            None if no variables get highlighted in this step.
            Else the 'timeline' provides the set of variables that are
            in the bag(s) under consideration. This function computes all other
            variables that are involved in this timestep using the 'edgelist'.

        colors : Iterable of color
            Colors to use for the graph parts.

        Returns
        -------
        None, but outputs the files with the graph for each timestep.

        """
        _filename = self.outfolder / file_basename
        LOGGER.info("Generating general-graph for '%s'", file_basename)
        vartag_n: str = var_name + '%d'
        # sfdp http://yifanhu.net/SOFTWARE/SFDP/index.html
        default_engine = 'sfdp'

        graph = Graph(
            graph_name,
            strict=True,
            engine=default_engine,
            graph_attr={
                'fontsize': str(fontsize),
                'overlap': 'false',
                'outputorder': 'edgesfirst',
                'K': '2'},
            node_attr={
                'fontcolor': str(fontcolor),
                'penwidth': str(penwidth),
                'style': 'filled',
                'fillcolor': 'white'})

        if do_sort_nodes:
            bodybaselen = len(graph.body)
            # 1: layout with circo
            graph.engine = 'circo'
            # 2: nodes in edges+extra_nodes make a circle
            nodes = sorted([vartag_n % n for n in set(
                itertools.chain(flatten(edges), extra_nodes))],
                key=lambda x: (len(x), x))
            for i, node in enumerate(nodes):
                graph.edge(str(nodes[i - 1]), str(node))
            # 3: reads in bytes!
            code_lines = graph.pipe('plain').splitlines()
            # 4: save the (sorted) positions
            assert code_lines[0].startswith(b'graph')
            node_positions = [line.split()[1:4] for line in code_lines[1:]
                              if line.startswith(b'node')]
            # 5: cut layout
            graph.body = graph.body[:bodybaselen]
            for line in node_positions:
                graph.node(line[0].decode(),
                           pos='%f,%f!' % (float(line[1]), float(line[2])))
            # 6: Engine uses previous positions
            graph.engine = 'neato'

        for (src, tar) in edges:
            graph.edge(vartag_n % src, vartag_n % tar)
        for nodeid in extra_nodes:
            graph.node(vartag_n % nodeid)

        bodybaselen = len(graph.body)

        for i, variables in enumerate(timeline, start=1):    # all timesteps
            # reset highlighting
            graph.body = graph.body[:bodybaselen]

            if variables is None:
                graph.render(
                    view=view,
                    format='svg',
                    filename=str(_filename) + str(i))
                continue

            for var in variables:
                graph.node(
                    vartag_n % var,
                    fillcolor=first_color,
                    style=first_style)

            # highlight edges between variables
            for (s, t) in edges:
                if s in variables and t in variables:
                    graph.edge(
                        vartag_n % s,
                        vartag_n % t,
                        color=third_color,
                        penwidth=str(penwidth))

            if do_adj_nodes:
                # set.difference accepts list as argument, "-" does not.
                edges = [set(edge) for edge in edges]
                adjacent = {
                    edge.difference(variables).pop() for edge in edges if len(
                        edge.difference(variables)) == 1}

                for var in adjacent:
                    graph.node(vartag_n % var,
                               color=second_color,
                               style=second_style)

            graph.render(view=view, format='svg',
                         filename=str(_filename) + str(i))

    def incidence(
            self,
            timeline: Iterable[Optional[List[int]]],
            num_vars: int,
            colors: List,
            edges: List,
            inc_file: str = 'IncidenceGraphStep',
            view: bool = False,
            fontsize: Union[str, int] = 16,
            penwidth: float = 2.2,
            basefill: str = 'white',
            sndshape: str = 'diamond',
            neg_tail: str = 'odot',
            var_name_one: str = '',
            var_name_two: str = '',
            column_distance: float = 0.5) -> None:
        """
        Creates the incidence graph emphasized for the given timeline.

        Parameters
        ----------
        timeline : Iterable of: None | [int...]
            None if no variables get highlighted in this step.
            Else the 'timeline' provides the set of variables that are
            in the bag(s) under consideration. This function computes all other
            variables that are involved in this timestep using the 'edgelist'.
        num_vars : int
            Count of variables that are used in the clauses.
        colors : Iterable of color
            Colors to use for the graph parts.
        inc_file : string
            Basis for the file created, gets appended with the step number.
        view : bool
            If true opens the created file after creation. Default is false.
        basefill : color
            Background color of all nodes. Default is 'white'.
        sndshape : string
            Description of the shape for nodes with the variables. Default diamond.
        neg_tail : string
            Description of the shape of the edge-tail indicating a
            negated variable. Default is 'odot'.
        column_distance : float
            Changes the distance between both partitions, measured in image-units.
            Default is 0.5

        Returns
        -------
        None, but outputs the files with the graph for each timestep.

        """
        _filename = self.outfolder / inc_file

        clausetag_n = var_name_one + '%d'
        vartag_n = var_name_two + '%d'

        g_incid = Graph(
            inc_file,
            strict=True,
            graph_attr={
                'splines': 'false',
                'ranksep': '0.2',
                'nodesep': str(float(column_distance)),
                'fontsize': str(
                    int(fontsize)),
                'compound': 'true'},
            edge_attr={
                'penwidth': str(float(penwidth)),
                'dir': 'back',
                'arrowtail': 'none'})
        with g_incid.subgraph(name='cluster_clause',
                              edge_attr={'style': 'invis'},
                              node_attr={'style': 'rounded,filled',
                                         'fillcolor': basefill}) as clauses:
            clauses.attr(label='clauses')
            clauses.edges([(clausetag_n % (i + 1), clausetag_n % (i + 2))
                           for i in range(len(edges) - 1)])

        g_incid.attr('node', shape=sndshape,
                     penwidth=str(float(penwidth)),
                     style='dotted')
        with g_incid.subgraph(name='cluster_ivar',
                              edge_attr={'style': 'invis'}) as ivars:
            ivars.attr(label='variables')
            ivars.edges([(vartag_n % (i + 1), vartag_n % (i + 2))
                         for i in range(num_vars - 1)])
            for i in range(num_vars):
                g_incid.node(vartag_n %
                             (i + 1), vartag_n %
                             (i + 1), color=colors[(i + 1) %
                                                   len(colors)])

        g_incid.attr('edge', constraint='false')

        for clause in edges:
            for var in clause[1]:
                if var >= 0:
                    g_incid.edge(clausetag_n % clause[0],
                                 vartag_n % var,
                                 color=colors[var % len(colors)])
                else:
                    g_incid.edge(clausetag_n % clause[0],
                                 vartag_n % -var,
                                 color=colors[-var % len(colors)],
                                 arrowtail=neg_tail)

        # make edgelist variable-based (varX, clauseY), ...
        #  var_cl_iter [(1, 1), (4, 1), ...
        var_cl_iter = tuple(flatten([[(x, y[0]) for x in y[1]]
                                     for y in edges]))

        bodybaselen = len(g_incid.body)
        for i, variables in enumerate(timeline, start=1):    # all timesteps

            # reset highlighting
            g_incid.body = g_incid.body[:bodybaselen]
            if variables is None:
                g_incid.render(view=view, format='svg',
                               filename=str(_filename) + str(i))
                continue

            emp_clause = {
                var_cl[1] for var_cl in var_cl_iter if abs(
                    var_cl[0]) in variables}

            emp_var = {abs(var_cl[0])
                       for var_cl in var_cl_iter if var_cl[1] in emp_clause}

            for var in emp_var:
                _vartag = vartag_n % abs(var)
                _style = 'solid,filled' if var in variables else 'dotted,filled'
                g_incid.node(
                    _vartag,
                    _vartag,
                    style=_style,
                    fillcolor='yellow')

            for clause in emp_clause:
                g_incid.node(
                    clausetag_n % clause,
                    clausetag_n % clause,
                    fillcolor='yellow')

            for edge in var_cl_iter:
                (var, clause) = edge

                _style = 'solid' if clause in emp_clause else 'dotted'
                _vartag = vartag_n % abs(var)

                if var >= 0:
                    g_incid.edge(clausetag_n % clause,
                                 _vartag,
                                 color=colors[var % len(colors)],
                                 style=_style)
                else:                                       # negated variable
                    g_incid.edge(clausetag_n % clause,
                                 _vartag,
                                 color=colors[-var % len(colors)],
                                 arrowtail='odot',
                                 style=_style)

            g_incid.render(
                view=view,
                format='svg',
                filename=str(_filename) + str(i))

    def call_svgjoin(self) -> None:
        """Analyzes content in data.svg_join for the call to svg_join."""
        sj_data = self.data.svg_join
        if not sj_data.base_names:
            LOGGER.warning(
                "svg_join data in JsonAPI contains no file-names to join.")
            return
        if isinstance(sj_data.base_names, str):
            sj_data.base_names = [sj_data.base_names]
        sj_data.num_images = int(sj_data.num_images)
        # Other arguments get handled directly in svgjoin for iterators etc.
        # Use default outfolder only if folder is None
        if sj_data.folder is None:
            updated_sj_data = asdict(sj_data)
            updated_sj_data["folder"] = self.outfolder
            svg_join(**updated_sj_data)
        else:
            svg_join(**asdict(sj_data))


def main(args: List[str]) -> None:
    """
    Main method running visualization for arguments in 'args'.

    Parameters
    ----------
    args : List[str]
        The array containing all (command-line) flags.

    Returns
    -------
    None
    """
    parser = get_parser(
        "Visualizing Dynamic Programming on Tree-Decompositions.")
    # possible to use stdin for the file.
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin,
                        help="Input file for the visualization "
                        "must conform with the 'JsonAPI.md'")
    parser.add_argument('outfolder',
                        help="Folder to output the visualization results")

    # get cmd-arguments
    options = parser.parse_args(args)

    logging_cfg(filename='logging.yml', loglevel=options.loglevel)
    LOGGER.info("Called with '%s'", options)

    infile = options.infile
    outfolder = options.outfolder
    if not outfolder:
        outfolder = 'outfolder'
    outfolder = Path(outfolder).resolve()

    LOGGER.info("Will read from '%s' and write to folder '%s'",
                infile.name, outfolder)
    visu = Visualization(infile=infile, outfolder=outfolder)
    visu.tree_dec_timeline()


def init():
    """Initialization that is executed at the time of the module import."""
    if __name__ == "__main__":
        sys.exit(main(sys.argv[1:]))  # call main function


init()
