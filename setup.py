# -*- coding: utf-8 -*-
import io
from setuptools import setup
from tdvisu.version import __version__ as version

def read_files(files):
    data = []
    for file in files:
        with io.open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)


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
