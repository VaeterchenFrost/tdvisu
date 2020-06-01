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

import json
import io
import itertools
import logging
from sys import stdin
from typing import Iterable, Iterator, TypeVar
from dataclasses import asdict

from graphviz import Digraph, Graph
from tdvisu.visualization_data import VisualizationData, IncidenceGraphData, GeneralGraphData
from tdvisu.version import __date__, __version__ as version

logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)s"
    "[%(filename)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__name__)


def read_json(json_data) -> dict:
    """
    Read json data into a callable object.
    Throws error if the parsed object has length 0.

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


_T = TypeVar('_T')


def flatten(iterable: Iterable[Iterable[_T]]) -> Iterator[_T]:
    """ Flatten at first level.

    Turn ex=[[1,2],[3,4]] into
    [1, 2, 3, 4]
    and [ex,ex] into
    [[1, 2], [3, 4], [1, 2], [3, 4]]
    """
    return itertools.chain.from_iterable(iterable)


class Visualization:
    """Holds and processes the information needed to provide dot-format
    and image output for the visualization
    of dynamic programming on tree decomposition.
    """

    def __init__(self, infile, outfolder) -> None:
        """Copy needed fields from arguments and create additional constants"""
        self.data: VisualizationData = self.inspect_json(infile)
        self.outfolder = outfolder

        self.tree_dec_digraph = None
        LOGGER.debug("Initialized: %s", self)

    @staticmethod
    def base_style(graph, node, color='white', penwidth='1.0') -> None:
        """Style the node with default fillcolor and penwidth."""
        graph.node(node, fillcolor=color, penwidth=penwidth)

    @staticmethod
    def emphasise_node(graph, node, color='yellow',
                       penwidth='2.5') -> None:
        """Emphasise node with a different fillcolor (default:'yellow')
        and penwidth (default:2.5).
        """
        if color:
            graph.node(node, fillcolor=color)
        if penwidth:
            graph.node(node, penwidth=penwidth)

    @staticmethod
    def style_hide_node(graph, node) -> None:
        """Make the node invisible during drawing."""
        graph.node(node, style='invis')

    @staticmethod
    def style_hide_edge(graph, source, target) -> None:
        """Make the edge source->target invisible during drawing."""
        graph.edge(source, target, style='invis')

    @staticmethod
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

    @staticmethod
    def solution_node(
            solution_table,
            toplabel='',
            bottomlabel='',
            transpose=False, linesmax=1000, columnsmax=50) -> str:
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

        if len(bottomlabel) > 0:
            result += '|' + bottomlabel

        return '{' + result + '}'

    def inspect_json(self, infile) -> VisualizationData:
        """Read and preprocess the needed data from the infile into VisualizationData."""
        LOGGER.debug("Reading from: %s", infile)
        visudata = read_json(infile)
        LOGGER.debug("Found keys: %s", visudata.keys())

        try:
            incid = visudata['incidenceGraph']
            general_graph = visudata['generalGraph']

            incid_data: IncidenceGraphData = None
            if incid:
                incid['edges'] = [[x['id'], x['list']] for x in incid['edges']]
                incid_data = IncidenceGraphData(**incid)
            visudata.pop('incidenceGraph')
            general_graph_data: GeneralGraphData = None
            if general_graph:
                general_graph_data = GeneralGraphData(**general_graph)
            visudata.pop('generalGraph')
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
        return VisualizationData(incidence_graph=incid_data,
                                 general_graph=general_graph_data,
                                 **visudata)

    def setup_tree_dec_graph(
            self,
            rankdir='BT',
            shape='box',
            fillcolor='white',
            style='rounded,filled',
            margin='0.11,0.01') -> None:
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
                                       self.bag_node(bagname, item['labels']))

        self.tree_dec_digraph.edges([(self.bagpre % str(first), self.bagpre % str(
            second)) for (first, second) in self.tree_dec['edgearray']])

    def forward_iterate_tdg(self, joinpre, solpre, soljoinpre) -> None:
        """Create the final positions of all nodes with solutions."""
        tdg = self.tree_dec_digraph                 # shorten name

        for i, node in enumerate(self.timeline):    # Create the positions
            if len(node) > 1:
                # solution to be displayed
                id_inv_bags = node[0]
                if isinstance(id_inv_bags, int):
                    last_sol = solpre % id_inv_bags
                    tdg.node(last_sol, self.solution_node(
                        *(node[1])), shape='record')

                    tdg.edge(self.bagpre % id_inv_bags, last_sol)

                else:                               # joined node with 2 bags
                    suc = self.timeline[i + 1][0]   # get the joined bags

                    LOGGER.debug('joining %s to %s ', node[0], suc)

                    id_inv_bags = tuple(id_inv_bags)
                    last_sol = soljoinpre % id_inv_bags
                    tdg.node(last_sol, self.solution_node(
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

    def backwards_iterate_tdg(self, joinpre, solpre, soljoinpre,
                              view=False) -> None:
        """Cut the single steps back and update emphasis acordingly."""
        tdg = self.tree_dec_digraph     # shorten name
        last_sol = ""

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
                self.base_style(tdg, bag)
                if last_sol:
                    self.style_hide_node(tdg, last_sol)
                    self.style_hide_edge(tdg, bag, last_sol)
                    last_sol = ""

            if len(node) > 1:
                # solution to be displayed
                if isinstance(id_inv_bags, int):
                    last_sol = solpre % id_inv_bags
                    self.emphasise_node(tdg, last_sol)
                    tdg.edge(self.bagpre % id_inv_bags, last_sol)
                else:  # joined node with 2 bags
                    id_inv_bags = tuple(id_inv_bags)
                    last_sol = soljoinpre % id_inv_bags
                    self.emphasise_node(tdg, last_sol)

            self.emphasise_node(tdg,
                                self.bagpre %
                                id_inv_bags if isinstance(
                                    id_inv_bags,
                                    int) else joinpre %
                                id_inv_bags)
            _filename = self.outfolder + self.data.td_file + '%d'
            tdg.render(
                view=view, format='svg', filename=_filename %
                (len(self.timeline) - i))

    def tree_dec_timeline(self, view=False) -> None:
        """Main-method for handling all construction of the timeline."""

        self.setup_tree_dec_graph()
        # Iterate labeldict

        self.basic_tdg()
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

        _timeline = []
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
        __incid = self.data.incidence_graph
        if __incid:
            if __incid.infer_primal or __incid.infer_dual:
                # prepare incid edges with abs:
                abs_clauses = [[cl[0], list(map(abs, cl[1]))]
                               for cl in __incid.edges]
            if __incid.infer_primal:
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
                    graph_name=__incid.primal_file,
                    file_basename=__incid.primal_file,
                    var_name=__incid.var_name_two)
                LOGGER.info("Created infered primal-graph")

            if __incid.infer_dual:
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
                    graph_name=__incid.dual_file,
                    file_basename=__incid.dual_file,
                    var_name=__incid.var_name_one)
                LOGGER.info("Created infered dual-graph")
            self.incidence(
                timeline=_timeline,
                inc_file=__incid.inc_file,
                num_vars=self.tree_dec['num_vars'],
                colors=self.data.colors, view=view,
                fontsize=__incid.fontsize,
                penwidth=__incid.penwidth,
                basefill=self.data.bagcolor,
                var_name_one=__incid.var_name_one,
                var_name_two=__incid.var_name_two,
                column_distance=__incid.column_distance)
            LOGGER.info(
                "Created incidence-graph for file='%s'",
                self.data.incidence_graph.inc_file)
        if self.data.general_graph:
            self.general_graph(timeline=_timeline, view=view,
                               **asdict(self.data.general_graph))
            LOGGER.info(
                "Created general-graph for file='%s'",
                self.data.general_graph.file_basename)

    def general_graph(
            self,
            timeline,
            edges,
            extra_nodes=tuple(),
            view=False,
            fontsize='20',
            fontcolor='black',
            penwidth='2.2',
            first_color='yellow',
            first_style='filled',
            second_color='green',
            second_style='dotted,filled',
            third_color='red',
            graph_name='graph',
            file_basename='graph',
            do_sort_nodes=True,
            do_adj_nodes=True,
            var_name='') -> None:
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
        _filename = self.outfolder + file_basename + '%d'
        LOGGER.info("Generating general-graph for '%s'", file_basename)
        vartag_n = var_name + '%d'
        # sfdp http://yifanhu.net/SOFTWARE/SFDP/index.html
        default_engine = 'sfdp'

        graph = Graph(graph_name, strict=True,
                      engine=default_engine,
                      graph_attr={'fontsize': fontsize, 'overlap': 'false',
                                  'outputorder': 'edgesfirst', 'K': '2'},
                      node_attr={'fontcolor': fontcolor,
                                 'penwidth': penwidth,
                                 'style': 'filled', 'fillcolor': 'white'})

        if do_sort_nodes:
            bodybaselen = len(graph.body)
            # 1: layout with circo
            graph.engine = 'circo'
            # 2: nodes in edges+extra_nodes make a circle
            nodes = sorted([vartag_n % n for n in set(
                itertools.chain(flatten(edges), extra_nodes))])
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
            # 5: Engine uses previous positions
            graph.engine = 'neato'

        for (s, t) in edges:
            graph.edge(vartag_n % s, vartag_n % t)
        for node in extra_nodes:
            graph.node(vartag_n % node)

        bodybaselen = len(graph.body)

        for i, variables in enumerate(timeline, start=1):    # all timesteps
            # reset highlighting
            graph.body = graph.body[:bodybaselen]

            if variables is None:
                graph.render(
                    view=view,
                    format='svg',
                    filename=_filename % i)
                continue

            for var in variables:
                graph.node(
                    vartag_n % var,
                    fillcolor=first_color,
                    style=first_style)

            # highlight edges between variables
            for (s, t) in edges:
                if (s in variables and t in variables):
                    graph.edge(
                        vartag_n % s,
                        vartag_n % t,
                        color=third_color,
                        penwidth=penwidth)

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

            graph.render(view=view, format='svg', filename=_filename % i)

    def incidence(
            self,
            timeline,
            num_vars,
            colors,
            inc_file='IncidenceGraphStep',
            view=False,
            fontsize=16,
            penwidth=2.2,
            basefill='white',
            sndshape='diamond',
            neg_tail='odot',
            var_name_one='',
            var_name_two='',
            column_distance=0.5) -> None:
        """
        Creates the incidence graph emphasized for the given timeline.

        Parameters
        ----------
        TIMELINE : Iterable of: None | [int...]
            None if no variables get highlighted in this step.
            Else the 'timeline' provides the set of variables that are
            in the bag(s) under consideration. This function computes all other
            variables that are involved in this timestep using the 'edgelist'.

        num_vars : int
            Count of variables that are used in the clauses.
        colors : Iterable of color
            Colors to use for the graph parts.

        Returns
        -------
        None, but outputs the files with the graph for each timestep.

        """
        _filename = self.outfolder + inc_file + '%d'

        clausetag_n = var_name_one + '%d'
        vartag_n = var_name_two + '%d'

        g_incid = Graph(
            inc_file,
            strict=True,
            graph_attr={
                'splines': 'false',
                'ranksep': '0.2',
                'nodesep': str(column_distance),
                'fontsize': str(
                    int(fontsize)),
                'compound': 'true'},
            edge_attr={
                'penwidth': str(penwidth),
                'dir': 'back',
                'arrowtail': 'none'})
        __incid = self.data.incidence_graph
        with g_incid.subgraph(name='cluster_clause',
                              edge_attr={'style': 'invis'},
                              node_attr={'style': 'rounded,filled',
                                         'fillcolor': basefill}) as clauses:
            clauses.attr(label='clauses')
            clauses.edges([(clausetag_n % (i + 1), clausetag_n % (i + 2))
                           for i in range(len(__incid.edges) - 1)])

        g_incid.attr('node', shape=sndshape, fontcolor='black',
                     penwidth=str(penwidth),
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

        for clause in __incid.edges:
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
        vcmapping = map(
            lambda y: map(
                lambda x: (x, y[0]),
                y[1]),
            __incid.edges)

        var_cl_iter = tuple(flatten(vcmapping))

        bodybaselen = len(g_incid.body)
        for i, variables in enumerate(timeline, start=1):    # all timesteps

            # reset highlighting
            g_incid.body = g_incid.body[:bodybaselen]
            if variables is None:
                g_incid.render(view=view, format='svg', filename=_filename % i)
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

            g_incid.render(view=view, format='svg', filename=_filename % i)


def main(args):
    """Main Function. Calling Visualization for arguments in 'args'."""

    # get loglevel
    try:
        loglevel = int(float(args.loglevel))
    except ValueError:
        loglevel = args.loglevel.upper()
    LOGGER.setLevel(loglevel)

    infile = args.infile
    outfolder = args.outfolder
    if not outfolder:
        outfolder = 'outfolder'
    outfolder = outfolder.replace('\\', '/')
    if not outfolder.endswith('/'):
        outfolder += '/'
    LOGGER.info("Will read from '%s' and write to folder '%s'",
                infile.name, outfolder)
    visu = Visualization(infile=infile, outfolder=outfolder)
    visu.tree_dec_timeline()


if __name__ == "__main__":

    import argparse

    PARSER = argparse.ArgumentParser(
        description="""
        Copyright (C) 2020 Martin Röbke
        This program comes with ABSOLUTELY NO WARRANTY
        This is free software, and you are welcome to redistribute it
        under certain conditions; see COPYING for more information.

        Visualizing Dynamic Programming on Tree-Decompositions.""",
        epilog="""Logging levels for python 3.8.2:
            CRITICAL: 50
            ERROR:    40
            WARNING:  30
            INFO:     20
            DEBUG:    10
            NOTSET:    0 (will traverse the logging hierarchy until a value is found)
            """,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # possible to use stdin for the file.
    PARSER.add_argument('infile', nargs='?',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default=stdin,
                        help="Input file for the visualization. "
                        "Must be a Json fulfilling the 'JsonAPI_v1.3.md'")
    PARSER.add_argument('outfolder',
                        help="Folder to output the visualization results.")
    PARSER.add_argument('--version', action='version',
                        version='%(prog)s ' + version + ', ' + __date__)
    PARSER.add_argument(
        '--loglevel',
        default='WARNING',
        help="set the minimal loglevel")

    # get cmd-arguments
    ARGS = PARSER.parse_args()
    # call main()
    main(ARGS)
