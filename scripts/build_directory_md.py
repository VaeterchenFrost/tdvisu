# -*- coding: utf-8 -*-
"""
Searching the directory for source-files and creating a markdown with its structure.

MIT License
Copyright (c) 2020 The Algorithms, Martin Röbke

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

"""


import os
from typing import Iterator
from urllib.parse import quote

URL_BASE = "https://github.com/VaeterchenFrost/tdvisu/blob/master"

AFFECTED_EXT = (
    ".py",
    ".ipynb",
)

EXCLUDED_FILENAMES = ("__init__.py",)


def good_file_paths(top_dir: str = ".") -> Iterator[str]:
    """Return relative path to files with extension in AFFECTED_EXT."""
    for dir_path, dir_names, filenames in os.walk(top_dir):
        dir_names[:] = [d for d in dir_names if d != "scripts" and d[0] not in "._"]
        for filename in filenames:
            if filename in EXCLUDED_FILENAMES:
                continue
            if os.path.splitext(filename)[1] in AFFECTED_EXT:
                normalized_path = os.path.normpath(dir_path)
                if normalized_path != ".":
                    yield os.path.join(normalized_path, filename)
                else:
                    yield filename


def md_prefix(nesting) -> str:
    """Creating the prefix for the specified nesting level."""
    return f"{nesting * '  '}*" if nesting else "\n##"


def print_path(old_path: str, new_path: str) -> str:
    """Print one header line in the markdown."""
    old_parts = old_path.split(os.sep)
    for i, new_part in enumerate(new_path.split(os.sep)):
        if i + 1 > len(old_parts) or old_parts[i] != new_part:
            if new_part:
                print(f"{md_prefix(i)} {new_part.replace('_', ' ').title()}")
    return new_path


def print_directory_md(top_dir: str = ".") -> None:
    """Print the markdown for files with selected extensions recursing top_dir."""
    old_path = ""
    for filepath in sorted(good_file_paths(top_dir)):
        filepath, filename = os.path.split(filepath)
        if filepath != old_path:
            old_path = print_path(old_path, filepath)
        indent = (filepath.count(os.sep) + 1) if filepath else 0
        url = "/".join(
            (URL_BASE, *[quote(part) for part in (filepath, filename) if part])
        )
        filename = os.path.splitext(filename.replace("_", " ").title())[0]
        print(f"{md_prefix(indent)} [{filename}]({url})")


if __name__ == "__main__":
    print_directory_md(".")
