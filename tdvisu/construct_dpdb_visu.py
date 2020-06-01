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

import json
import abc
import logging
import pathlib

from time import sleep
from configparser import ConfigParser

import psycopg2 as pg

from tdvisu.dijkstra import bidirectional_dijkstra as find_path
from tdvisu.dijkstra import convert_to_adj
from tdvisu.reader import TwReader
from tdvisu.visualization import flatten
from tdvisu.version import __date__, __version__ as version


logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s"
    "[%(filename)s:%(lineno)d] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING)

LOGGER = logging.getLogger(__name__)


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


def read_cfg(cfg_file, section) -> dict:
    """Read the config file and return the result.

    Works for both .ini and .json files but
    assumes json-format if the ending is NOT .ini
    """
    if pathlib.Path(cfg_file).suffix.lower() == '.ini':
        iniconfig = ConfigParser()
        iniconfig.read(cfg_file)
        result = dict()
        result['host'] = iniconfig.get(section, 'host', fallback='localhost')
        result['port'] = iniconfig.getint(section, 'port', fallback=5432)
        result['database'] = iniconfig.get(
            section, 'database', fallback='logicsem')
        result['user'] = iniconfig.get(section, 'user', fallback='postgres')
        result['password'] = iniconfig.get(section, 'password')
        result['application_name'] = iniconfig.get(
            section, 'application_name', fallback='dpdb-admin')
        return {section: result}

    # default behaviour
    with open(cfg_file) as jsonfile:
        return json.load(jsonfile)


def config(filename='database.ini', section='postgresql') -> dict:
    """Return the database config as JSON"""
    cfg = read_cfg(filename, section)
    if section in cfg:
        db_config = cfg[section]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    LOGGER.info("Read db_config['%s'] from '%s'", section, filename)
    return db_config


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
        raise NotImplementedError
        
    @abc.abstractmethod
    def read_edgearray(self) -> list:
        """Return the edges between the bags."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_labeldict(self) -> list:
        """Construct the corresponding labels for each bag."""
        raise NotImplementedError

    @abc.abstractmethod
    def read_timeline(self, edgearray) -> list:
        """Read from td_node_status and the edearray to
            - create the timeline of the solving process
            - construct the path and solution-tables used during solving.
        """
        raise NotImplementedError


class DpdbSharpSatVisu(IDpdbVisuConstruct):
    """Implementation of the JSON-Construction for the SharpSat problem."""

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
                'generalGraph': False,
                'tdTimeline': timeline,
                'treeDecJson': tree_dec_json}

    def read_num_vars(self) -> int:
        """
        Select the number of "vertices" in the graph.

        Returns
        -------
        int
            Number of "vertices" in the graph.

        """
        with self.connection.cursor() as cur:  # create a cursor
            cur.execute(
                "SELECT num_vertices FROM "
                "public.problem WHERE id=%s", (self.problem,))
            self.num_vars = cur.fetchone()[0]
            assert isinstance(self.num_vars, int)
            return self.num_vars

    def read_clauses(self) -> list:
        """Return the clauses used for satiyfiability.
        Variables are counted from 1 and negative if negated in the clause.
        For example:

            [{
                "id" : 1,
                "list" : [ 1, -4, 6 ]
            },...]
        """
        with self.connection.cursor() as cur:  # create a cursor
            try:
                cur.execute(
                    f"SELECT * FROM public.p{self.problem}_sat_clause")
            except pg.ProgrammingError:
                LOGGER.error(
                    "dpdb.py SHARPSAT NEEDS TO BE RUN WITH '--store-formula'!")
                raise
            result = cur.fetchall()
            result_cleaned = [[pos if elem else -pos for pos, elem in
                               enumerate(line, 1) if elem is not None]
                              for line in result]
            clauses_edges = [{'id': i, 'list': item}
                             for (i, item) in enumerate(result_cleaned, 1)]
            return clauses_edges

    def read_labeldict(self) -> list:
        """
        Read from '_td_bag' the edges and 'td_node_status' tables the labels
        for the bags.

        Returns
        -------
        list
            The filled labeldict for visualization.

        """
        with self.connection.cursor() as cur:  # create a cursor
            labeldict = []
            # check bag numbering:
            cur.execute(
                f"SELECT bag FROM public.p{self.problem}_td_bag group by bag")
            bags = sorted(list(flatten(cur.fetchall())))
            LOGGER.debug("bags: %s", bags)
            for bag in bags:
                cur.execute(
                    f"SELECT node FROM public.p{self.problem}_td_bag WHERE bag=%s", (bag,))
                nodes = list(flatten(cur.fetchall()))
                cur.execute(
                    "SELECT start_time,end_time-start_time "
                    f"FROM public.p{self.problem}_td_node_status WHERE node=%s", (bag,))
                start_time, dtime = cur.fetchone()
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
            cur.execute(
                f"SELECT node FROM public.p{self.problem}_td_node_status ORDER BY start_time")
            order_solved = list(flatten(cur.fetchall()))
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
                #  deepcode ignore Sqli: general query, inserting integers
                cur.execute(
                    "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS "
                    f"WHERE TABLE_NAME = 'p{self.problem}_td_node_{bag}'")
                column_names = list(flatten(cur.fetchall()))
                LOGGER.debug("column_names %s", column_names)
                # get solutions
                #  deepcode ignore Sqli: general query, inserting integers
                cur.execute(
                    f"SELECT * FROM public.p{self.problem}_td_node_{bag}")
                solution_raw = cur.fetchall()
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
        with self.connection.cursor() as cur:  # create a cursor
            cur.execute(
                f"SELECT node,parent FROM public.p{self.problem}_td_edge")
            result = cur.fetchall()
            return result

    @staticmethod
    def footer(lines):
        """Returns the footer for solution bags."""
        return "sum: " + str(sum([li[-1] for li in lines]))


class DpdbMinVcVisu(DpdbSharpSatVisu):
    """Implementation of the JSON-Construction for the MinVC problem.
    Borrowing methods from DpdbSharpSatVisu.
    """

    def __init__(self, db, problem, intermed_nodes, tw_file=None):
        super().__init__(db, problem, intermed_nodes)
        self.tw_file = tw_file

    def read_clauses(self):
        raise NotImplementedError(
            self.__class__.__name__ +
            " can not read_clauses!")

    @staticmethod
    def footer(lines):
        """Returns the footer for solution bags."""
        return "min-size: " + str(min([li[-1] for li in lines]))

    def read_twfile(self):
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

    def construct(self):
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

        generalGraph = {'edges': self.read_twfile()} if self.tw_file else False

        timeline = self.read_timeline(edgearray)
        return {'incidenceGraph': False,
                'generalGraph': generalGraph,
                'tdTimeline': timeline,
                'treeDecJson': tree_dec_json}


def connect() -> pg.extensions.connection:
    """Connect to the PostgreSQL database server using the params from config"""

    conn = None
    try:
        # read connection parameters
        params = config()
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


def create_json(problem: int, tw_file=None, intermed_nodes=False) -> dict:
    """Create the JSON for the specified Problem instance."""
    try:
        with connect() as connection:
            # get type of problem
            with connection.cursor() as cur:
                cur.execute("SELECT name,type,num_bags FROM "
                            "public.problem WHERE id=%s", (problem,))
                (name, ptype, num_bags) = cur.fetchone()

            # select the valid constructor for the problem
            constructor: IDpdbVisuConstruct

            if ptype == 'SharpSat':
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


if __name__ == "__main__":

    import argparse

    PARSER = argparse.ArgumentParser(
        description="""
        Copyright (C) 2020 Martin Röbke
        This program comes with ABSOLUTELY NO WARRANTY
        This is free software, and you are welcome to redistribute it
        under certain conditions; see COPYING for more information.

        Extracts Information from https://github.com/hmarkus/dp_on_dbs runs
        for further visualization.""",
        epilog="""Logging levels for python 3.8.2:
            CRITICAL: 50
            ERROR:    40
            WARNING:  30
            INFO:     20
            DEBUG:    10
            NOTSET:    0 (will traverse the logging hierarchy until a value is found)
            """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    PARSER.add_argument('problemnumber', type=int,
                        help="problem-id in the postgres-database.")
    PARSER.add_argument('--twfile',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help="tw-File containing the edges of the graph - "
                        "obtained from dpdb with option --gr-file GR_FILE.")
    PARSER.add_argument('--loglevel', default='INFO', help="default:'INFO'")
    PARSER.add_argument(
        '--outfile',
        default='dbjson%d.json',
        help="default:'dbjson%%d.json'")
    PARSER.add_argument('--pretty', action='store_true',
                        help="Pretty-print the JSON.")
    PARSER.add_argument(
        '--inter-nodes',
        action='store_true',
        help="Calculate path between successive nodes during the evaluation order.")
    PARSER.add_argument('--version', action='version',
                        version='%(prog)s ' + version + ', ' + __date__)

    # get cmd-arguments
    args = PARSER.parse_args()
    LOGGER.info('%s', args)
    # get loglevel
    try:
        loglevel = int(float(args.loglevel))
    except ValueError:
        loglevel = args.loglevel.upper()
    LOGGER.setLevel(loglevel)
    problem_ = args.problemnumber
    # get twfile if supplied
    try:
        tw_file_ = args.twfile
    except AttributeError:
        tw_file_ = None
    RESULTJSON = create_json(problem=problem_, tw_file=tw_file_)
    # build json filename, can be supplied with problem-number
    try:
        outfile = args.outfile % problem_
    except TypeError:
        outfile = args.outfile
    LOGGER.info("Output file-name: %s", outfile)
    with open(outfile, 'w') as file:
        json.dump(
            RESULTJSON,
            file,
            sort_keys=True,
            indent=2 if args.pretty else None,
            ensure_ascii=False)
        LOGGER.debug("Wrote to %s", file)
