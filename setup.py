# -*- coding: utf-8 -*-
"""Describing local installs or distribution of the package tdvisu."""

from setuptools import setup
from tdvisu.version import __version__ as version


def read_files(files, delim: str = "\n") -> str:
    r"""
    Concatenate the content of one or more files joined by a delimiter.

    Parameters
    ----------
    files : Iterable of single files
        Every file is a text or byte string giving the name
        (and the path if the file isn't in the current working directory)
         of the file to be opened or an integer file descriptor
         of the file to be wrapped.
    delim : str, optional
        The delimiter to be inserted between the contents. The default is "\n".

    Returns
    -------
    str
        The concatenated string.
    """
    data = []
    for file in files:
        with open(file, encoding='utf-8') as handle:
            data.append(handle.read())
    return delim.join(data)


long_description = read_files(['README.md', 'CHANGELOG.md'])


description = "Visualizing Dynamic Programming on Tree Decompositions."

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Multimedia :: Graphics :: Presentation']

tests_require = ['unittest_expander']

setup(name="tdvisu",
      version=version,
      description=description,
      long_description=long_description,
      long_description_content_type='text/markdown',
      url="https://github.com/VaeterchenFrost/tdvisu",
      author="Martin Röbke",
      author_email="martin.roebke@mailbox.tu-dresden.de",
      license='GPLv3',
      packages=['tdvisu'],
      platforms='any',
      install_requires=['graphviz', 'psycopg2', 'python-benedict'],
      extras_require={'test': tests_require},
      classifiers=classifiers,
      keywords='graph visualization dynamic-programming msol-solver')
