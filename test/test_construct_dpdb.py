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

from pathlib import Path
from tdvisu.construct_dpdb_visu import (read_cfg, db_config, DEFAULT_DBCONFIG,
                                        IDpdbVisuConstruct, DpdbSharpSatVisu,
                                        DpdbSatVisu, DpdbMinVcVisu)

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
