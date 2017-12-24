#!usr/bin/env python
__author__ = "Min Sung Ahn"
__email__ = "aminsung@gmail.com"
__copyright__ = "Copyright 2016 RoMeLa"
__date__ = "August 23, 2016"

__version__ = "0.0.1"
__status__ = "Final"

import mmap
import collections

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
        self._attr = collections.defaultdict(lambda: collections.defaultdict(int))

        self.curr_data = np.empty((1,1))
        self.memsize = 0 # Size of the memory segment

        self.initialize = init

    def add_blocks(self, name, data):
        '''Given name and data, the block will be added to the segment
        Currently, it supports numpy.arrays and strings'''
        self._attr[name]['name'] = name
        # If type of data is numpy array
        if type(data) is np.ndarray:
            # > Create data and size
            self.datatype = np.ndarray
            self._attr[name]['data'] = data
            self._attr[name]['size'] = data.size * data.itemsize
            self._attr[name]['shape'] = data.shape # It is assumed to be an NxN array
        elif type(data) is str:
            # > Else, create data and string size
            self.datatype = str
            self._attr[name]['data'] = data.encode('utf8') # We assume it is a string and encode it UTF-8
            self._attr[name]['size'] = len(data)
            self._attr[name]['shape'] = (1,1)

    def update_total_segment(self):
        '''Parses the entire memory segment size. To be run after all blocks are added.'''
        self.curr_data = None
        self.memsize = 0
        for k, v in self._attr.iteritems():
            if k != 'mem' and k != 'lock':
                self._attr[k]['midx'] = self.memsize # Easy tracker for indexing of where the memory starts for k
                self.memsize += self._attr[k]['size']
                if self.datatype is np.ndarray:
                    if self.curr_data is None:
                        self.curr_data = self._attr[k]['data'].reshape(-1,1)
                    else:
                        # If numpy array, make it a very long array of column 1
                        self.curr_data = np.concatenate((self.curr_data, self._attr[k]['data'].reshape(-1,1)), axis=0)

    def connect_segment(self):
        '''Function that actually creates the memory block'''
        # Make sure to update the total segment first!
        self.update_total_segment()

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
            self._attr['mem'] = mmap.mmap(mem.fd, mem.size)
            self._attr['lock'] = posix_ipc.Semaphore(path_name + "_lock", posix_ipc.O_CREX)
            self._attr['lock'].release()

            # Close the open FD
            mem.close_fd()
        else:
            # Create the shared memory, semaphore blocks and map to a dict
            mem = posix_ipc.SharedMemory(path_name + "_mem")
            self._attr['mem'] = mmap.mmap(mem.fd, mem.size)
            self._attr['lock'] = posix_ipc.Semaphore(path_name + "_lock")
            self._attr['lock'].release()

            mem.close_fd()

        self.initialize = False

    def set(self, val):
        '''Update the memory segment with a new set of values
           Input should be a dictionary with keys as:
                name
                    data
        '''
        # Once lock is retrieved, write to mem:
        with self._attr['lock']:
            self._write_to_mem(val)

    def get(self):
        '''Get the data that is currently in the shared memory and parse for the user
        Note that maps memory AND semaphore are also returned. # TODO: Maybe not return this...'''
        # Numpy version
        # === Retrieve the data
        with self._attr['lock']:
            data = self._read_from_mem()
        # === Parse the data
        for k, v in self._attr.iteritems():
            if k != 'mem' and k != 'lock':
                idx_a = self._attr[k]['midx']/self._attr[k]['data'].itemsize
                idx_b = idx_a + self._attr[k]['size']/self._attr[k]['data'].itemsize
                self._attr[k]['data'] = data[idx_a:idx_b,0,None]
                self._attr[k]['data'].reshape(self._attr[k]['shape'])

        retdict = self._attr.copy()
        del retdict['mem']
        del retdict['lock']
        return retdict

    def _write_to_mem(self, val):
        '''Write the data to the memory block'''
        for k, v in val.iteritems():
            if k in self._attr:
                self._attr[k]['data'] = val[k]['data']
            else:
                self._attr[k]['data'] = val[k]['data']
                self._attr[k]['size'] = val[k]['data'].size * val[k]['data'].itemsize
                self._attr[k]['shape'] = val[k]['data'].shape
        self.update_total_segment()
        # Update self.curr_data to a long vector
        self._attr['mem'].seek(0)
        self._attr['mem'].write(self.curr_data.data)

    def _read_from_mem(self):
        self._attr['mem'].seek(0)
        return np.ndarray(shape=(self.memsize/self.curr_data.itemsize,1), buffer=self._attr['mem'])