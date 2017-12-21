#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 5, 2016"

__version__ = "0.0.1"
__status__ = "Prototype"

import time
import collections

import numpy as np

import pyshmxtreme as shmxs

# Configure shared memory segments and data shapes
RobotState = collections.defaultdict(lambda: collections.defaultdict(int))
RobotState['rleg'] = np.zeros((6,1))

# RobotState['rleg']['shape'] = (6,1)
# RobotState['lleg']['shape'] = (6,1)

# Initialize the shared memory segments
State = shmx.SHMSegment(RobotState, 'State')

# Shared memory is to be run independently
if __name__ == '__main__':
    while True:
        time.sleep(2)
        print time.clock()