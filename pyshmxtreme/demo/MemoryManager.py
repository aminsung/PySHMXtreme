#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2017 RoMeLa"
__date__ = "December 25, 2017"

__version__ = "0.0.1"
__status__ = "Prototype"

'''
MemoryManager is a macro file to your favorite memory segments.

Pre-generate your shared memory segments before proceeding with using them in the rest of your scripts. 
'''

import numpy as np
import time

import pyshmxtreme.SHMSegment as shmx

# ===== Create shared memory segments
# Time Data
TIME_STATE = shmx.SHMSegment(robot_name='ALPHRED', seg_name='TIME_STATE', init=False)
TIME_STATE.add_blocks(name='time', data=np.zeros((1,1)))

# Joint Data
JOINT_STATE = shmx.SHMSegment(robot_name='ALPHRED', seg_name='JOINT_STATE', init=False)
JOINT_STATE.add_blocks(name='limb1_pos', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb1_vel', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb1_acc', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb2_pos', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb2_vel', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb2_acc', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb3_pos', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb3_vel', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb3_acc', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb4_pos', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb4_vel', data=np.zeros((3,1)))
JOINT_STATE.add_blocks(name='limb4_acc', data=np.zeros((3,1)))

# Vision data
VISION_STATE = shmx.SHMSegment(robot_name='ALPHRED', seg_name='VISION_STATE', init=False)
IMG_C = 80
IMG_R = 60
VISION_STATE.add_blocks(name='xyz', data=np.zeros((IMG_R, IMG_C, 3)))
VISION_STATE.add_blocks(name='depth', data=np.zeros((IMG_R,IMG_C)))
VISION_STATE.add_blocks(name='pos', data=np.zeros((IMG_R,IMG_C, 2)))

def init():
    '''Init if main'''
    TIME_STATE.initialize = True
    JOINT_STATE.initialize = True
    VISION_STATE.initialize = True

def connect():
    '''Connect and create segment'''
    TIME_STATE.connect_segment()
    JOINT_STATE.connect_segment()
    VISION_STATE.connect_segment()

if __name__ == '__main__':
    init()
    connect()
else:
    connect()