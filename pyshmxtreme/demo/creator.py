#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

import time

import numpy as np

import pyshmxtreme.SHMSegment as shmx

# /********** NUMPY Implementation *******************************************/
# Create an instance of creating a shared memory segment
robot_state = shmx.SHMSegment(robot_name='robot_name', seg_name='state', init=True)

# Create memory containers to be used throughout your processes
robot_state.add_blocks(name='rleg', data=np.arange(6).reshape((6,1)))
robot_state.add_blocks(name='rarm', data=np.arange(7).reshape((7,1)))

# Connect and create the segments
robot_state.connect_segment()


print("[!] Creating segment done!")

while True:
    time.sleep(1)
    # Read data to see if I get the right things
    ret_data = robot_state.get()
    print("Returned data: \n{}".format(ret_data['rarm']['data'].reshape(1,-1)))