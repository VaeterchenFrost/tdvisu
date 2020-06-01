# -*- coding: utf-8 -*-
"""Testing version.py

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
from datetime import date
import re
import unittest
from tdvisu.version import __date__, __version__ as version


class TestVersion(unittest.TestCase):
    """Testing fields in version."""

    def test_semantic_version(self):
        """Test the version-format with https://semver.org/spec/v2.0.0.html."""
        self.assertIsInstance(version, str)
        regex = (r"^(?P<major>0|[1-9]\d*)\."
                 r"(?P<minor>0|[1-9]\d*)\."
                 r"(?P<patch>0|[1-9]\d*)"
                 r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
                 r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))"
                 "?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")
        result = re.fullmatch(regex, version)
        msg = f"The version {version} does not adhere to semantic versioning!"
        self.assertIsNotNone(result, msg)

    def test_date(self):
        """The date should be 'YYYY-MM-DD' isoformat to be fully portable."""
        self.assertIsInstance(__date__, str)
        # Is it an existing date?
        try:
            date.fromisoformat(__date__)
        except ValueError as err:
            msg = f"""The date {__date__} is not in the format YYYY-MM-DD!
                    ValueError: {err}
                    Today would be: '{date.today().isoformat()}'"""
            self.fail(msg)


if __name__ == '__main__':
    unittest.main()
