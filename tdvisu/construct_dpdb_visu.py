# -*- coding: utf-8 -*-
"""
Construct visualization-JSON from dpdb-database results.

See https://www.postgresqltutorial.com/postgresql-python/connect/
and reference
https://github.com/VaeterchenFrost/dp_on_dbs.git

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

import abc
import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import List, Optional, Tuple

import psycopg2 as pg
from psycopg2 import sql

from tdvisu.dijkstra import bidirectional_dijkstra as find_path
from tdvisu.reader import TwReader
from tdvisu.utilities import convert_to_adj, flatten, get_parser
from tdvisu.utilities import logging_cfg, read_yml_or_cfg

LOGGER = logging.getLogger('construct_dpdb_visu.py')

DEFAULT_DBCONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "logicsem",
    "user": "postgres",
    "application_name": "dpdb-admin"
}

PSYCOPG2_8_5_TASTATUS = {
    pg.extensions.TRANSACTION_STATUS_IDLE:
        ('TRANSACTION_STATUS_IDLE ',
         '(The session is idle and there is no current transaction.)'),

        pg.extensions.TRANSACTION_STATUS_ACTIVE:
        ('TRANSACTION_STATUS_ACTIVE ',
         '(A command is currently in progress.)'),

        pg.extensions.TRANSACTION_STATUS_INTRANS:
        ('TRANSACTION_STATUS_INTRANS ',
         '(The session is idle in a valid transaction block.)'),

        pg.extensions.TRANSACTION_STATUS_INERROR:
        ('TRANSACTION_STATUS_INERROR ',
         '(The session is idle in a failed transaction block.)'),

        pg.extensions.TRANSACTION_STATUS_UNKNOWN:
        ('TRANSACTION_STATUS_UNKNOWN ',
         '(Reported if the connection with the server is bad.)')
}


def good_db_status() -> tuple:
    """Any good db status to proceed."""
    return (pg.extensions.TRANSACTION_STATUS_IDLE,
            pg.extensions.TRANSACTION_STATUS_INTRANS)


def read_cfg(cfg_file, section: str, prefer_cfg: bool = False) -> dict:
    """Read the config file and return the result of one section."""
    try:
        file_content = read_yml_or_cfg(cfg_file, prefer_cfg=prefer_cfg)
        content = dict(file_content[section])
        LOGGER.debug(
            "Found keys %s in %s[%s]", content.keys(), cfg_file, section)
    except (OSError, AttributeError, TypeError) as err:
        LOGGER.warning("Encountered %s while reading config '%s' section '%s'",
                       err, cfg_file, section, exc_info=True)
        content = {}
    return content


def db_config(filename: str = 'database.ini',
              section: str = 'postgresql') -> dict:
    """Return the database config as JSON"""
    file = Path(__file__).parent / filename
    LOGGER.info("Read db_config['%s'] from '%s'", section, file.resolve())
    cfg = read_cfg(file, section)
    return {**DEFAULT_DBCONFIG, **cfg}


def query_problem(cursor, problem: int) -> str:  # pragma: no cover
    """Query type from public.problem for one problem."""
    cursor.execute("SELECT type FROM "
                   "public.problem WHERE id=%s", (int(problem),))
    result = cursor.fetchone()[0]
    return result


def query_num_vars(cursor, problem: int) -> int:  # pragma: no cover
    """Query num_vertices from public.problem for one problem."""
    cursor.execute(
        "SELECT num_vertices FROM public.problem WHERE id=%s", (int(problem),))
    result = cursor.fetchone()[0]
    return result


def query_sat_clause(cursor, problem: int) -> List[Tuple[Optional[bool]]]:  # pragma: no cover
    """Query sat-clauses for one problem."""
    try:
        cursor.execute(
            sql.SQL("SELECT * FROM public.p{}_sat_clause").format(sql.Literal(int(problem))))
    except pg.ProgrammingError:
        LOGGER.error(
            "dpdb.py *SAT needs to be run with '--store-formula'!")
        raise
    result = cursor.fetchall()
    return result


def query_td_bag_grouped(cursor, problem: int) -> List[List[int]]:  # pragma: no cover
    """Query bag-ids for one problem."""
    cursor.execute(
        sql.SQL("SELECT bag FROM public.p{}_td_bag GROUP BY bag").format(
            sql.Literal(int(problem))))
    result = cursor.fetchall()
    return result


def query_td_node_status(
        cursor, problem: int, bag: int) -> Tuple[datetime, timedelta]:  # pragma: no cover
    """Query details about the status of one node.
    Currently start_time and end_time-start_time."""
    cursor.execute(
        sql.SQL(
            "SELECT start_time,end_time-start_time "
            "FROM public.p{}_td_node_status WHERE node=%s").format(
            sql.Literal(int(problem))), (int(bag),))
    result = cursor.fetchone()
    return result


def query_td_bag(cursor, problem: int, bag: int) -> List[Tuple[int]]:  # pragma: no cover
    """Query nodes included in one bag."""
    cursor.execute(
        sql.SQL("SELECT node FROM public.p{}_td_bag WHERE bag=%s").format(
            sql.Literal(int(problem))), (int(bag),))
    result = cursor.fetchall()
    return result


def query_td_node_status_ordered(cursor, problem: int) -> List[Tuple[int]]:  # pragma: no cover
    """Query bags ordered by 'start_time'."""
    cursor.execute(
        sql.SQL("SELECT node FROM public.p{}_td_node_status ORDER BY start_time").format(
            sql.Literal(int(problem))))
    result = cursor.fetchall()
    return result


def query_column_name(cursor, problem: int, bag: int) -> List[Tuple[str]]:  # pragma: no cover
    """Query column names for one bag."""
    cursor.execute(
        sql.SQL(
            "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = 'p{}_td_node_{}'").format(
            sql.Literal(int(problem)),
            sql.Literal(int(bag))))
    result = cursor.fetchall()
    return result


def query_bag(cursor, problem: int, bag: int) -> List[Tuple[Optional[bool]]]:  # pragma: no cover
    """Query solution data for one bag."""
    cursor.execute(sql.SQL(
        "SELECT * FROM public.p{}_td_node_{}").format(sql.Literal(int(problem)), sql.Literal(int(bag))))
    result = cursor.fetchall()
    return result


def query_edgearray(cursor, problem: int) -> List[Tuple[int, int]]:  # pragma: no cover
    """Query edges between bags for one problem."""
    cursor.execute(
        sql.SQL("SELECT node,parent FROM public.p{}_td_edge").format(
            sql.Literal(int(problem))))
    result = cursor.fetchall()
    return result


class IDpdbVisuConstruct(metaclass=abc.ABCMeta):
    """Interface for parsing database results from dynamic programming
    into the JSON used for visualizing the solution steps
    on the tree decomposition.
    See details for i-face impl in https://realpython.com/python-interface/
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'construct') and
                callable(subclass.construct) and
                hasattr(subclass, 'read_labeldict') and
                callable(subclass.read_labeldict) and
                hasattr(subclass, 'read_timeline') and
                callable(subclass.read_timeline) and
                hasattr(subclass, 'read_edgearray') and
                callable(subclass.read_edgearray) or
                NotImplemented)

    @abc.abstractmethod
    def construct(self) -> dict:
        """Return the constructed Json."""
        raise NotImplementedError   # pragma: no cover

    @abc.abstractmethod
    def read_edgearray(self) -> list:
        """Return the edges between the bags."""
        raise NotImplementedError   # pragma: no cover

    @abc.abstractmethod
    def read_labeldict(self) -> list:
        """Construct the corresponding labels for each bag."""
        raise NotImplementedError   # pragma: no cover

    @abc.abstractmethod
    def read_timeline(self, edgearray) -> list:
        """Read from td_node_status and the edearray to
            - create the timeline of the solving process
            - construct the path and solution-tables used during solving.
        """
        raise NotImplementedError  # pragma: no cover


class DpdbSharpSatVisu(IDpdbVisuConstruct):
    """Implementation of the JSON-construction for the SharpSat problem."""

    def __init__(self, db: pg.extensions.connection,
                 problem: int, intermed_nodes: bool):
        """db : psycopg2.connection
            database to read from.
        problem : int
            index of the problem.
        intermed_nodes : bool
            if True calculates the shortest path between successive nodes.
        """
        LOGGER.debug("Creating %s for problem %d.",
                     self.__class__.__name__, problem)
        self.problem = problem
        self.intermed_nodes = intermed_nodes
        self.num_vars = None

        # wait for good connection
        status = db.get_transaction_status()
        sleeptimer = 0.5
        while status not in good_db_status():
            logging.warning("Waiting %fs for DB connection in status %s",
                            sleeptimer, PSYCOPG2_8_5_TASTATUS[status])
            sleep(sleeptimer)
            status = db.get_transaction_status()

        self.connection = db

    def construct(self) -> dict:
        """
        Construct the Json calling several helper methods.

        Returns
        -------
        dict
            The Json for the visualization-API.

        """

        clauses_edges = self.read_clauses()
        incidence_graph = {
            "var_name_one": 'c_',
            "var_name_two": 'v_',
            "infer_primal": True,
            "edges": clauses_edges}

        # create tree_dec_json
        labeldict = self.read_labeldict()
        edgearray = self.read_edgearray()
        tree_dec_json = {
            "bagpre": "bag %s",
            "edgearray": edgearray,
            "labeldict": labeldict,
            "num_vars": self.read_num_vars()}

        timeline = self.read_timeline(edgearray)

        return {'incidenceGraph': incidence_graph,
                'tdTimeline': timeline,
                'treeDecJson': tree_dec_json}

    def read_num_vars(self) -> int:
        """
        Select the number of vertices in the graph.

        Returns
        -------
        int
            Number of vertices in the graph.

        """
        with self.connection.cursor() as cur:  # create a cursor
            self.num_vars = query_num_vars(cur, self.problem)
            assert isinstance(self.num_vars, int)
            return self.num_vars

    def read_clauses(self) -> list:
        """Return the clauses used for satisfiability.
        Variables are counted from 1 and negative if negated in the clause.
        For example:

            [{
                "id" : 1,
                "list" : [ 1, -4, 6 ]
            },...]
        """
        with self.connection.cursor() as cur:
            result = query_sat_clause(cur, self.problem)
            result_cleaned = [[pos if elem else -pos for pos, elem in
                               enumerate(line, 1) if elem is not None]
                              for line in result]
            clauses_edges = [{'id': i, 'list': item}
                             for (i, item) in enumerate(result_cleaned, 1)]
            return clauses_edges

    def read_labeldict(self) -> list:
        """
        Read edges from '_td_bag' and the labels from 'td_node_status' for the bags.

        Returns
        -------
        list
            The filled labeldict for visualization.

        """
        with self.connection.cursor() as cur:  # create a cursor
            labeldict = []
            # check bag numbering:
            bags = sorted(
                list(
                    flatten(
                        query_td_bag_grouped(
                            cur,
                            self.problem))))
            LOGGER.debug("bags: %s", bags)
            for bag in bags:
                nodes = list(flatten(query_td_bag(cur, self.problem, bag)))
                start_time, dtime = query_td_node_status(
                    cur, self.problem, bag)
                labeldict.append(
                    {'id': bag, 'items': nodes, 'labels':
                     [str(nodes),
                      "dtime=%.4fs" % dtime.total_seconds(),
                      # start_time.strftime("%D %T")
                      ]})
            return labeldict

    def read_timeline(self, edgearray) -> list:
        """
        Read from td_node_status and the edearray to
        - create the timeline of the solving process
        - construct the path and solution-tables used during solving.

        Parameters
        ----------
        edgearray : array of pairs of bagids
            Representing the tree-like structure between all bag-ids.
            It is assumed that all ids are included in this array.
            Example: [(2, 1), (3, 2), (4, 2), (5, 4)]

        Returns
        -------
        result : array
            array of bagids and eventually solution-tables.

        """
        with self.connection.cursor() as cur:  # create a cursor
            timeline = list()
            adj = convert_to_adj(edgearray) if self.intermed_nodes else {}
            order_solved = list(
                flatten(
                    query_td_node_status_ordered(
                        cur, self.problem)))
            # tour sol -> through result nodes along the edges

            if self.intermed_nodes:
                last = order_solved[-1]
                startpath = find_path(adj, last, order_solved[0])
                timeline = [[bag] for bag in startpath[1]]
            else:
                timeline.append([order_solved[0]])
            # add the other bags in order_solved to the timeline
            last = order_solved[0]
            for bag in order_solved:
                if self.intermed_nodes:
                    path = find_path(adj, last, bag)
                    for intermed in path[1][1:]:
                        timeline.append([intermed])
                # query column names
                column_names = list(
                    flatten(
                        query_column_name(
                            cur,
                            self.problem,
                            bag)))
                LOGGER.debug("column_names %s", column_names)
                # get solutions
                solution_raw = query_bag(cur, self.problem, bag)
                LOGGER.debug("solution_raw %s", solution_raw)
                # check for nulled variables - assuming whole columns are
                # nulled:
                columns_notnull = [column_names[i] for i, x in
                                   enumerate(solution_raw[0]) if x is not None]
                solution = [bag,
                            [[columns_notnull,
                              *[[int(v) for v in row if v is not None]
                                for row in solution_raw]],
                             "sol bag " + str(bag),
                             self.footer(solution_raw),
                             True]]
                timeline.append(solution)
                last = bag
            return timeline

    def read_edgearray(self):
        """Read from _td_edge the edges between bags."""
        with self.connection.cursor() as cur:
            return query_edgearray(cur, self.problem)

    @staticmethod
    def footer(lines) -> str:
        """Returns the footer for solution bags."""
        return "sum: " + str(sum([li[-1] for li in lines]))


class DpdbSatVisu(DpdbSharpSatVisu):
    """Implementation of the JSON-construction for the SAT problem.
    Removing the solution sum in bottom-label.
    """
    @staticmethod
    def footer(lines) -> str:
        """Returns empty footer."""
        return ""


class DpdbMinVcVisu(DpdbSharpSatVisu):
    """Implementation of the JSON-construction for the MinVC problem."""

    def __init__(self, db, problem, intermed_nodes, tw_file=None):
        super().__init__(db, problem, intermed_nodes)
        self.tw_file = tw_file

    def read_clauses(self):
        raise NotImplementedError(
            self.__class__.__name__ +
            " can not read_clauses!")

    @staticmethod
    def footer(lines) -> str:
        """Returns the footer for solution bags."""
        return "min-size: " + str(min([li[-1] for li in lines]))

    def read_twfile(self) -> list:
        """
        Use TwReader.from_file to read the edges for the generalGraph.

        Returns
        -------
        List
            The edges as an list of pairs of vertices.

        """
        LOGGER.info("Reading from %s", self.tw_file)
        try:
            reader = TwReader.from_filewrapper(self.tw_file)
        except Exception as error:
            LOGGER.error("Problem while reading from self.tw_file: %s", error)
            raise error

        # create list so that it is JSON serializable
        return list(reader.edges)

    def construct(self) -> dict:
        """
        Construct the Json calling several helper methods.

        Returns
        -------
        dict
            The Json for the visualization-API.

        """
        # create tree_dec_json
        labeldict = self.read_labeldict()
        edgearray = self.read_edgearray()
        tree_dec_json = {
            'bagpre': "bag %s",
            'edgearray': edgearray,
            'labeldict': labeldict,
            'num_vars': self.read_num_vars()}

        general_gr = {'edges': self.read_twfile()} if self.tw_file else False

        timeline = self.read_timeline(edgearray)
        return {'generalGraph': general_gr,
                'tdTimeline': timeline,
                'treeDecJson': tree_dec_json}


def connect() -> pg.extensions.connection:
    """Connect to the PostgreSQL database server using the params from config."""

    conn = None
    try:
        # read connection parameters
        params = db_config(filename='Archive/database.json')
        db_name = params['database']
        LOGGER.info("Connecting to the PostgreSQL database '%s'...", db_name)
        conn = pg.connect(**params)
        with conn.cursor() as cur:  # create a cursor
            # display the PostgreSQL database server version
            LOGGER.info('PostgreSQL database version:')
            cur.execute('SELECT version()')
            db_version = cur.fetchone()
            LOGGER.info(db_version)
    except (Exception, pg.DatabaseError) as error:
        LOGGER.error(error)
        raise error
    return conn


def create_json(
        problem: int,
        tw_file=None,
        intermed_nodes: bool = False) -> dict:
    """Create the JSON for the specified problem instance."""

    try:
        with connect() as connection:
            # get type of problem
            with connection.cursor() as cur:
                ptype = query_problem(cur, problem)

            # select the valid constructor for the problem
            constructor: IDpdbVisuConstruct

            if ptype == 'Sat':
                constructor = DpdbSatVisu(
                    connection, problem, intermed_nodes)
            elif ptype == 'SharpSat':
                constructor = DpdbSharpSatVisu(
                    connection, problem, intermed_nodes)
            elif ptype == 'VertexCover':
                constructor = DpdbMinVcVisu(
                    connection, problem, intermed_nodes, tw_file)

            LOGGER.info("Using %s for type=%s",
                        constructor.__class__.__name__, ptype)
            LOGGER.info("Constructing Json...")
            return constructor.construct()
    except (Exception, pg.DatabaseError) as error:
        LOGGER.error(error)
        raise error
    return {}


def main(args: List[str]) -> None:
    """
    Main method running construct_dpdb_visu for arguments in 'args'.

    Parameters
    ----------
    args : List[str]
        The array containing all (command-line) flags.

    Returns
    -------
    None
    """
    parser = get_parser("Extracts Information from "
                        "https://github.com/hmarkus/dp_on_dbs runs "
                        "for further visualization.")

    parser.add_argument('problemnumber', type=int,
                        help="selected problem-id in the postgres-database.")
    parser.add_argument('--twfile',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help="tw-file containing the edges of the graph - "
                        "obtained from dpdb with option --gr-file GR_FILE.")
    parser.add_argument('--outfile', default='dbjson%d.json',
                        help="default:'dbjson%%d.json'")
    parser.add_argument('--pretty', action='store_true',
                        help="pretty-print the JSON.")
    parser.add_argument('--inter-nodes', action='store_true',
                        help="calculate and animate the shortest path between "
                        "successive bags in the order of evaluation.")
    # get cmd-arguments
    options = parser.parse_args(args)

    logging_cfg(filename='logging.yml', loglevel=options.loglevel)
    LOGGER.info("Called with '%s'", options)
    problem_ = options.problemnumber
    # get twfile if supplied
    try:
        tw_file_ = options.twfile
    except AttributeError:
        tw_file_ = None

    # create JSON
    result_json = create_json(problem=problem_, tw_file=tw_file_)
    try:    # build json filename, can be supplied with problem-number
        outfile = options.outfile % problem_
    except TypeError:
        outfile = options.outfile
    LOGGER.info("Output file-name: %s", outfile)
    with open(outfile, 'w') as file:
        json.dump(
            result_json,
            file,
            sort_keys=True,
            indent=2 if options.pretty else None,
            ensure_ascii=False)
        LOGGER.debug("Wrote to %s", file)


def init():
    """Initialization that is executed at the time of the module import."""
    if __name__ == "__main__":
        sys.exit(main(sys.argv[1:]))  # call main function


init()
