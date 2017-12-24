#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

import time

import collections
import numpy as np

import pyshmxtreme.SHMSegment as shmx

# /********** NUMPY Implementation *******************************************/
# Create an instance of creating a shared memory segment
robot_state = shmx.SHMSegment(robot_name='robot_name', seg_name='state', init=False)

# Create memory containers to be used throughout your processes
robot_state.add_blocks(name='rleg', data=np.arange(6).reshape((6,1)))
robot_state.add_blocks(name='rarm', data=np.arange(7).reshape((7,1)))

# Connect to the segments create
robot_state.connect_segment()

print("Conencted!")

data = collections.defaultdict(lambda: collections.defaultdict(int))

while True:
    datain = float(raw_input('Input float64 >> '))

    data['rarm']['data'] = datain*np.ones((7,1))
    data['rleg']['data'] = (datain**2)*np.ones((6,1))
    robot_state.set(data)