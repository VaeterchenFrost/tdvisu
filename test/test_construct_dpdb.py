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
from tdvisu.construct_dpdb_visu import read_cfg, db_config

DIR = Path(__file__).parent


def test_db_config():
    result = read_cfg(DIR / 'database.ini', 'postgresql', True)
    assert result == {'application_name': 'dpdb-admin',
                      'database': 'logicsem',
                      'host': 'localhost',
                      'password': 'XXX',
                      'port': '5432',
                      'user': 'postgres'}
