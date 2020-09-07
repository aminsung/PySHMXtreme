#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

import mmap
import collections
import threading

import numpy as np
import posix_ipc

class SHMSegment(object):
    def __init__(self, robot_name='robotname', seg_name='segname', init=False):
        '''
        Create a new shared memory segment that will nicely keep all the different information organized
        in a block of memory.

        :params robot_name: Name of robot
        :params seg_name: Root name of the memory segment
        :params init: Indicate whether this instance will create the segment, or just connect to it
        '''
        self.robot_name = robot_name
        self._seg_name = seg_name
        self._attr = []

        self._mem_addr = None
        self._mem_lock = None

        self.curr_data = np.empty((1,1))
        self.memsize = 0 # Size of the memory segment

        self.initialize = init

    def add_blocks(self, name, data):
        '''Given name and data, the block will be added to the segment
        Currently, it supports numpy.arrays and strings'''
        block = {}
        block['name'] = name
        # If type of data is numpy array
        if type(data) is np.ndarray:
            # > Create data and size
            self.datatype = np.ndarray
            block['data'] = data
            block['size'] = data.size * data.itemsize
            block['shape'] = data.shape
            block['midx'] = self.memsize
            self.memsize += block['size']
        elif type(data) is np.chararray:
            # > Else, create data and string size
            self.datatype = np.chararray
            block['data'] = data
            block['size'] = data.size * data.itemsize
            block['shape'] = data.shape
            block['midx'] = self.memsize
            self.memsize += block['size']

        self._attr.append(block)

    def update_total_segment(self):
        '''Parses the entire memory segment size. To be run after all blocks are added.'''
        self.curr_data = None
        for idx in range(len(self._attr)):
            if self.curr_data is None:
                self.curr_data = self._attr[idx]['data'].reshape(-1,1)
            else:
                # If numpy array, make it a very long array of column 1
                self.curr_data = np.concatenate((self.curr_data, self._attr[idx]['data'].reshape(-1,1)), axis=0)

    def connect_segment(self):
        '''Function that actually creates the memory block'''
        # Make sure to update the total segment first!
        self.update_total_segment()

        # You can't mmap a size zero segment
        if self.memsize == 0:
            raise ValueError("Min says: You are trying to create an empty memory block! Add blocks of memory via add_block() method!")

        # Path name to be used in /dev/shm
        path_name = "{}_{}".format(self.robot_name, self._seg_name)

        # Close all shared memory if they already exist
        if self.initialize:
            # If the instance is to initialize the segment...
            try:
                posix_ipc.unlink_shared_memory(path_name + "_mem")
                posix_ipc.unlink_semaphore(path_name + "_lock")
            except posix_ipc.ExistentialError:
                pass

            # Create the shared memory, semaphore blocks and map it
            mem = posix_ipc.SharedMemory(path_name + "_mem", posix_ipc.O_CREX, size=self.memsize)
            self._mem_addr = mmap.mmap(mem.fd, mem.size)
            self._mem_lock = posix_ipc.Semaphore(path_name + "_lock", posix_ipc.O_CREX)
            self._mem_lock.release()

            # Close the open FD
            mem.close_fd()
        else:
            # Create the shared memory, semaphore blocks and map to a dict
            mem = posix_ipc.SharedMemory(path_name + "_mem")
            self._mem_addr = mmap.mmap(mem.fd, mem.size)
            self._mem_lock = posix_ipc.Semaphore(path_name + "_lock")
            self._mem_lock.release()

            mem.close_fd()

        self.initialize = False

    def set(self, val):
        '''
            Update the memory segment with a new set of values
            Input should be a dictionary with key, value as:
                val = {name : data}
        '''
        # Once lock is retrieved, write to mem:
        with self._mem_lock:
            self._write_to_mem(val)

    def get(self):
        '''Get the data that is currently in the shared memory and parse for the user'''
        # Numpy version
        with self._mem_lock:
            data = self._read_from_mem()

        retdict = {}

        for idx in range(len(self._attr)):
            idx_a = self._attr[idx]['midx']//self._attr[idx]['data'].itemsize
            idx_b = idx_a + self._attr[idx]['size']//self._attr[idx]['data'].itemsize
            self._attr[idx]['data'] = data[idx_a:idx_b, 0, None].reshape(self._attr[idx]['shape'], order='F')
            # self._attr[idx]['data'] = data[idx_a:idx_b,0,None]
            # self._attr[idx]['data'].shape = self._attr[idx]['shape']
            retdict[self._attr[idx]['name']] = self._attr[idx]['data']

        return retdict

    def get_seg_name(self):
        return self._seg_name


    def _write_to_mem(self, val):
        '''Write the data to the memory block'''
        for idx in range(len(self._attr)):
            if self._attr[idx]['name'] in val:
                self._attr[idx]['data'] = val[self._attr[idx]['name']]

        self.update_total_segment()
        self._mem_addr.seek(0)
        self._mem_addr.write(self.curr_data.data)


    def _read_from_mem(self):
        '''Read from memory'''
        self._mem_addr.seek(0)
        if self.datatype == np.ndarray:
            return np.ndarray(shape=(self.memsize//self.curr_data.itemsize,1), buffer=self._mem_addr)
        elif self.datatype == np.chararray:
            return np.chararray(shape=(self.memsize//self.curr_data.itemsize,1), buffer=self._mem_addr)

