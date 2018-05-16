#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

from setuptools import setup

setup(
	name='PySHMXtreme',
	version='0.0.1',
	author='Min Sung Ahn',
	author_email='aminsung@ucla.edu',
	packages=['pyshmxtreme'],
        install_requires=[
            'numpy',
            'posix_ipc',
        ],
	)
