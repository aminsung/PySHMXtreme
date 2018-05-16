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
	data['time'] = np.array([[time.time()]])
	MemoryManager.TIME_STATE.set(data)
	print("Time set: {}".format(data['time']))