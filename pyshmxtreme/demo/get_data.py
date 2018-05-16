#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2017 RoMeLa"
__date__ = "December 25, 2017"

__version__ = "0.0.1"
__status__ = "Prototype"

import time

import numpy as np

import MemoryManager

data = {}
while True:
	data = MemoryManager.TIME_STATE.get()
	dt = time.time() - data['time']
	print("Hz: {}".format(1/dt))
