# -*- coding: utf-8 -*-
"""
Testing construct_dpdb_visu.py


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
import datetime

from pathlib import Path
import psycopg2 as pg

from tdvisu.construct_dpdb_visu import (read_cfg, db_config, DEFAULT_DBCONFIG,
                                        IDpdbVisuConstruct, DpdbSharpSatVisu,
                                        DpdbSatVisu, DpdbMinVcVisu, main)

DIR = Path(__file__).parent
SECTION = 'postgresql'


def test_db_config():
    """Test reading the database configuration from the test file."""
    result = read_cfg(DIR / 'database.ini', SECTION, True)
    assert result == {'application_name': 'dpdb-admin',
                      'host': 'localhost',
                      'password': 'XXX',
                      'port': '123',
                      'user': 'postgres'
                      }, "should be able to read from ini file"

    result = db_config(DIR / 'database.ini', SECTION)
    assert result == {'application_name': 'dpdb-admin',
                      'database': DEFAULT_DBCONFIG['database'],
                      'host': 'localhost',
                      'password': 'XXX',
                      'port': '123',
                      'user': 'postgres'
                      }, "should complete 'database' with default."


def test_db2_config():
    """Test should use defaults when file not found."""
    fixed_defaults = db_config(DIR / 'database2.ini', SECTION)
    assert fixed_defaults == DEFAULT_DBCONFIG


def test_db_passwd_config():
    """Test should add password from file to defaults."""
    insert_passwd = db_config(DIR / 'db_password.ini', SECTION)
    assert insert_passwd == {'application_name': 'dpdb-admin',
                             'database': 'logicsem',
                             'host': 'localhost',
                             'password': 'XXX',
                             'port': 5432,
                             'user': 'postgres'
                             }


def test_problem_interface():
    """Derived classes should implement the interface."""
    assert issubclass(DpdbSatVisu, IDpdbVisuConstruct)
    assert issubclass(DpdbSharpSatVisu, IDpdbVisuConstruct)
    assert issubclass(DpdbMinVcVisu, IDpdbVisuConstruct)


def test_main(mocker, tmp_path):
    """Test behaviour of construct_dpdb_visu.main"""

    mock_connect = mocker.patch('tdvisu.construct_dpdb_visu.pg.connect')
    ta_status = mock_connect.return_value.__enter__.return_value.get_transaction_status
    ta_status.return_value = pg.extensions.TRANSACTION_STATUS_IDLE

    query_problem = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_problem',
        return_value=('Sat',))
    query_num_vars = mocker.patch('tdvisu.construct_dpdb_visu.query_num_vars',
                                  return_value=8)
    query_td_node_status_ordered = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_td_node_status_ordered',
        return_value=[(3,), (5,), (4,), (2,), (1,)])
    query_sat_clause = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_sat_clause',
        return_value=[(True, None, None, True, None, True, None, None, None, None),
                      (True, None, None, None, False,
                       None, None, None, None, None),
                      (False, None, None, None, None,
                       None, True, None, None, None),
                      (None, True, True, None, None, None, None, None, None, None),
                      (None, True, None, None, True, None, None, None, None, None),
                      (None, True, None, None, None,
                       False, None, None, None, None),
                      (None, None, True, None, None,
                       None, None, False, None, None),
                      (None, None, None, True, None,
                       None, None, False, None, None),
                      (None, None, None, False, None,
                       True, None, None, None, None),
                      (None, None, None, False, None, None, True, None, None, None)])

    query_td_bag_grouped = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_td_bag_grouped', return_value=[[1, 2, 3, 4, 5]])
    query_td_node_status = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_td_node_status',
        return_value=(
            "2020-07-13 02:06:18.053880",
            datetime.timedelta(
                microseconds=768)))
    query_td_bag = mocker.patch('tdvisu.construct_dpdb_visu.query_td_bag',
                                return_value=[(1,), (2,), (4,), (6,)])
    query_column_name = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_column_name', return_value=[
            ('v1',), ('v2',), ('v4',), ('v6',)])
    query_bag = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_bag',
        return_value=[(False, None, False, None),
                      (True, None, True, None),
                      (False, None, True, None),
                      (True, None, False, None)])

    query_edgearray = mocker.patch(
        'tdvisu.construct_dpdb_visu.query_edgearray', return_value=[
            (2, 1), (3, 2), (4, 2), (5, 4)])

    parser = argparse.ArgumentParser()
    parser.add_argument('problemnumber', type=int,
                        help="selected problem-id in the postgres-database.")
    parser.add_argument('--twfile',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help="tw-file containing the edges of the graph - "
                        "obtained from dpdb with option --gr-file GR_FILE.")
    parser.add_argument('--loglevel', help="set the minimal loglevel for root")
    parser.add_argument('--outfile', default='dbjson%d.json',
                        help="default:'dbjson%%d.json'")
    parser.add_argument('--pretty', action='store_true',
                        help="pretty-print the JSON.")
    parser.add_argument('--inter-nodes', action='store_true',
                        help="calculate and animate the shortest path between "
                        "successive bags in the order of evaluation.")

    # set cmd-arguments
    outfile = str(tmp_path / 'test_main.json')
    _args = parser.parse_args(['1', '--outfile', outfile])
    # one mocked run
    main(_args)

    # Assertions
    mock_connect.assert_called_once()
    query_problem.assert_called_once()
    query_num_vars.assert_called_once()
    query_td_bag_grouped.assert_called_once()
    query_sat_clause.assert_called_once()
    query_td_node_status_ordered.assert_called_once()
    query_edgearray.assert_called_once()
    assert query_bag.call_count == 5
    assert query_column_name.call_count == 5
    assert query_td_bag.call_count == 5
    assert query_td_node_status.call_count == 5
